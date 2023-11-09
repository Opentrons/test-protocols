metadata = {
    'protocolName': 'Immunoprecipitation by Dynabeads - 96-well setting on Opentrons Flex with 96 channel pipette',
    'author': 'Boren Lin, Opentrons',
    'description': 'The protocol automates immunoprecipitation to isolate a protein of interest from liquid samples (up to 96 samples) by using protein A– or protein G–coupled magnetic beads.'
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

########################

NUM_SAMPLES = 96

ASP_HEIGHT = 0.6 #original = .2
MIX_SPEEND = 2000
MIX_SEC = 10

INCUBATION_ON_DECK = 1
# Yes:1; No:0
# if on deck:
INCUBATION_SPEEND = 1000
INCUBATION_MIN = 10

MAG_DELAY_MIN = 1

BEADS_VOL = 50
AB_VOL = 50
SAMPLE_VOL = 200
WASH_TIMES = 3
WASH_VOL = 200
ELUTION_VOL = 50

WASTE_VOL_MAX = 275000

READY_FOR_SDSPAGE = 0
# YES: 1; NO: 0

USE_GRIPPER = True

waste_vol_chk = 0

ABR_TEST                = True
if ABR_TEST == True:
    DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack
else:
    DRYRUN              = False          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = True 


#########################

def run(ctx):

    # load labware
    
    sample_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B2', 'samples')
    beads_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'C3', 'beads') 
    ab_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B3', 'ab')
    elu_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'A1', 'elution buffer')
    wash_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B1', 'wash buffer')

    waste_res = ctx.load_labware('nest_1_reservoir_290ml', 'D2', 'waste')

    if READY_FOR_SDSPAGE == 0:
        tips_elu = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'A2', adapter='opentrons_flex_96_tiprack_adapter')
        tips_elu_loc = tips_elu.wells()[:95]
    tips_reused = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'C2', adapter='opentrons_flex_96_tiprack_adapter')
    tips_reused_loc = tips_reused.wells()[:95]
    p1000 = ctx.load_instrument('flex_96channel_1000', 'left') 
    
    h_s = ctx.load_module('heaterShakerModuleV1', 'D1')
    h_s_adapter = h_s.load_adapter('opentrons_96_deep_well_adapter')
    working_plate = h_s_adapter.load_labware("nest_96_wellplate_2ml_deep", 'wokring plate')

    if READY_FOR_SDSPAGE == 0:
        temp = ctx.load_module('Temperature Module Gen2', 'D3')
        final_plate = temp.load_labware('opentrons_96_deep_well_adapter_nest_wellplate_2ml_deep', 'final plate')

    mag = ctx.load_module('magneticBlockV1', 4)

    # liquids
    samples = sample_plate.wells()[:NUM_SAMPLES]  ## 1
    beads = beads_plate.wells()[:NUM_SAMPLES]  ## 2
    ab = ab_plate.wells()[:NUM_SAMPLES]  ## 3 
    elu = elu_plate.wells()[:NUM_SAMPLES]  ## 4
    wash = wash_plate.wells()[:NUM_SAMPLES]  ## 5
    waste = waste_res.wells()[0]
    working_cols = working_plate.wells()[:NUM_SAMPLES]  ## 6
    if READY_FOR_SDSPAGE == 0: final_cols = final_plate.wells()[:NUM_SAMPLES]
    
    def transfer(vol1, start, end, liquid, drop_height=-20):   
        start_loc = start[0]
        end_loc = end[0]
        if liquid == 4 or liquid == 6: p1000.pick_up_tip(tips_elu_loc[0])   
        else: p1000.pick_up_tip(tips_reused_loc[0])  
        if liquid == 2: p1000.mix(10, vol1*0.75, start_loc.bottom(z=ASP_HEIGHT), rate = 2)
        p1000.aspirate(vol1, start_loc.bottom(z=ASP_HEIGHT), rate = 2)
        p1000.air_gap(10)
        p1000.dispense(vol1+10, end_loc.top(z=drop_height), rate = 2)
        p1000.blow_out()
        p1000.return_tip()
                  
    def mix(speend, time):
        ctx.comment('\n\n\n~~~~~~~~Shake to mix~~~~~~~~\n')
        h_s.set_and_wait_for_shake_speed(rpm=speend)
        ctx.delay(seconds=time)
        h_s.deactivate_shaker()

    def discard(vol2, start):
        global waste_vol
        global waste_vol_chk
        if waste_vol_chk >= WASTE_VOL_MAX: 
            ctx.pause('Empty Liquid Waste')
            waste_vol_chk = 0   
        waste_vol = 0
        start_loc = start[0]
        end_loc = waste
        p1000.pick_up_tip(tips_reused_loc[0]) 
        p1000.aspirate(vol2, start_loc.bottom(z=ASP_HEIGHT), rate = 0.3)
        p1000.air_gap(10)
        p1000.dispense(vol2+10, end_loc.top(z=-5), rate = 2)
        p1000.blow_out()
        p1000.return_tip()
        waste_vol = vol2 * NUM_SAMPLES
        waste_vol_chk = waste_vol_chk + waste_vol

    # protocol

    ## Add beads, samples and antibody solution
    h_s.open_labware_latch()
    ctx.pause('Move the Working Plate to the Shaker')
    h_s.close_labware_latch()

    transfer(BEADS_VOL, beads, working_cols, 2)

    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Magnet')
    ctx.move_labware(labware = working_plate,
                     new_location = mag,
                     use_gripper=USE_GRIPPER
                     )
    h_s.close_labware_latch()
    ctx.delay(minutes=MAG_DELAY_MIN)
    discard(BEADS_VOL*1.1, working_cols)

    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Shaker')
    ctx.move_labware(labware = working_plate,
                     new_location = h_s_adapter,
                     use_gripper=USE_GRIPPER
                     )
    h_s.close_labware_latch()

    transfer(SAMPLE_VOL, samples, working_cols, 1)
    transfer(AB_VOL, ab, working_cols, 3)

    h_s.set_and_wait_for_shake_speed(rpm=MIX_SPEEND)
    ctx.delay(seconds=MIX_SEC)

    if INCUBATION_ON_DECK == 1:
        h_s.set_and_wait_for_shake_speed(rpm=INCUBATION_SPEEND)
        ctx.delay(seconds=INCUBATION_MIN*60)
        h_s.deactivate_shaker()
        h_s.open_labware_latch()

    else:
        # incubation off deck 
        h_s.deactivate_shaker()
        h_s.open_labware_latch()
        ctx.pause('Seal the Plate')
        ctx.pause('Remove the Seal, Move the Plate to Shaker')

    #ctx.pause('Move the Working Plate to the Magnet')
    ctx.move_labware(labware = working_plate,
                     new_location = mag,
                     use_gripper=USE_GRIPPER
                     )
    h_s.close_labware_latch()

    ctx.delay(minutes=MAG_DELAY_MIN)
    vol_total = SAMPLE_VOL + AB_VOL
    discard(vol_total*1.1, working_cols)

    ## Wash
    for x in range(WASH_TIMES):
        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Shaker')
        ctx.move_labware(labware = working_plate,
                         new_location = h_s_adapter,
                         use_gripper=USE_GRIPPER
                         )
        h_s.close_labware_latch()

        transfer(WASH_VOL, wash, working_cols, 5)
        mix(MIX_SPEEND, MIX_SEC)

        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Magnet')
        ctx.move_labware(labware = working_plate,
                         new_location = mag,
                         use_gripper=USE_GRIPPER
                         )
        h_s.close_labware_latch()
        ctx.delay(minutes=MAG_DELAY_MIN)
        discard(WASH_VOL*1.1, working_cols)

    ## Elution      
    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Shaker')
    ctx.move_labware(labware = working_plate,
                     new_location = h_s_adapter,
                     use_gripper=USE_GRIPPER
                     )
    h_s.close_labware_latch()

    transfer(ELUTION_VOL, elu, working_cols, 4)
    if READY_FOR_SDSPAGE == 1:
        ctx.pause('Seal the Working Plate')
        h_s.set_and_wait_for_temperature(70)
        mix(MIX_SPEEND, MIX_SEC)
        ctx.delay(minutes=10)
        h_s.deactivate_heater()
        h_s.open_labware_latch()
        ctx.pause('Protocol Complete')

    elif READY_FOR_SDSPAGE == 0:
        mix(MIX_SPEEND, MIX_SEC)
        ctx.delay(minutes=2)
        temp.set_temperature(4)

        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Magnet')
        ctx.move_labware(labware = working_plate,
                        new_location = mag,
                        use_gripper=USE_GRIPPER
                        )
        h_s.close_labware_latch()
        ctx.delay(minutes=MAG_DELAY_MIN)
        transfer(ELUTION_VOL*1.1, working_cols, final_cols, 6, -5)
        ctx.pause('Protocol Complete')
        temp.deactivate()