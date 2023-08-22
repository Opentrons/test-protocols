metadata = {
    'protocolName': 'Immobilized Metal Affinity Chromatography by Ni-NTA Magnetic Agarose Beads - 96-well setting on Opentrons Flex',
    'author': 'Boren Lin, Opentrons',
    'description': 'The protocol automates immobilized metal affinity chromatography (IMAC) using Ni-NTA magnetic agarose beads to isolate a protein of interest from liquid samples (up to 96 samples).'
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.15"
}

########################

NUM_COL = 12

ASP_HEIGHT = 0.2
MIX_SPEEND = 2000
MIX_SEC = 10
ELUTION_SPEEND = 1000
ELUTION_MIN = 10

INCUBATION_ON_DECK = 0
# Yes:1; No:0
# if on deck:
INCUBATION_SPEEND = 1000
INCUBATION_MIN = 60

MAG_DELAY_MIN = 2

BEADS_PRELOAD = 1
# beads pre-loaded by plate prep protocol
# Yes: 1; No: 0
BEADS_VOL = 100
EQUILIBRATION_VOL1 = 400
EQUILIBRATION_VOL2 = 500
SAMPLE_VOL = 500
WASH_TIMES = 2
WASH_VOL = 500
ELUTION_TIMES = 1
ELUTION_VOL = 250

WASTE_VOL_MAX = 125000

COOLING_DELAY_MIN = 3

MAG_PLATE_SLOT = 4
USE_GRIPPER = True

#########################

def run(ctx):

    # load labware 
    sample_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 9, 'samples')
    if BEADS_PRELOAD == 0: beads_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 7, 'beads')
    eql_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 8, 'equilibration buffer')
    wash_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 6, 'wash buffer')
    elution_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 11, 'elution buffer')
    waste_res = ctx.load_labware('nest_1_reservoir_195ml', 2, 'waste')
 
    tips_reused = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', 5)
    tips_reused_loc = tips_reused.wells()[:96]
    tips_elu = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', 10, 'elution tips')
    tips_elu_loc = tips_elu.wells()[:96]
    p1000 = ctx.load_instrument('p1000_multi_gen3', 'left') 

    h_s = ctx.load_module('heaterShakerModuleV1',1)
    working_plate = h_s.load_labware("nest_96_wellplate_2ml_deep", 'working plate') 

    temp = ctx.load_module('Temperature Module Gen2', 3)
    final_plate = temp.load_labware('nest_96_wellplate_2ml_deep', 'final plate')

    # liquids
    samples = sample_plate.rows()[0][:NUM_COL]
    if BEADS_PRELOAD == 0: beads = beads_res.rows()[0][:NUM_COL] # reagent 2
    eql = eql_res.rows()[0][:NUM_COL]
    wash = wash_res.rows()[0][:NUM_COL]
    elu = elution_res.rows()[0][:NUM_COL] # reagent 1
    waste = waste_res.wells()[0]
    
    working_cols = working_plate.rows()[0][:NUM_COL]
    final_cols = final_plate.rows()[0][:NUM_COL]

    def grip_offset(action, item, slot=None):
        """Grip offset."""
        from opentrons.types import Point
        # EDIT these values
        # NOTE: we are still testing to determine our software's defaults
        #       but we also expect users will want to edit these
        _pick_up_offsets = {
            "deck": Point(),
            "mag-plate": Point(),
            "heater-shaker": Point(z=1.0),
            "temp-module": Point(),
            "thermo-cycler": Point(),
        }
        # EDIT these values
        # NOTE: we are still testing to determine our software's defaults
        #       but we also expect users will want to edit these
        _drop_offsets = {
            "deck": Point(),
            "mag-plate": Point(z=0.5),
            "heater-shaker": Point(),
            "temp-module": Point(),
            "thermo-cycler": Point(),
        }
        # do NOT edit these values
        # NOTE: these values will eventually be in our software
        #       and will not need to be inside a protocol
        _hw_offsets = {
            "deck": Point(),
            "mag-plate": Point(z=34.5),
            "heater-shaker-right": Point(z=2.5),
            "heater-shaker-left": Point(z=2.5),
            "temp-module": Point(z=5.0),
            "thermo-cycler": Point(z=2.5),
        }
        # make sure arguments are correct
        action_options = ["pick-up", "drop"]
        item_options = list(_hw_offsets.keys())
        item_options.remove("heater-shaker-left")
        item_options.remove("heater-shaker-right")
        item_options.append("heater-shaker")
        if action not in action_options:
            raise ValueError(
                f'"{action}" not recognized, available options: {action_options}'
            )
        if item not in item_options:
            raise ValueError(
                f'"{item}" not recognized, available options: {item_options}'
            )
        if item == "heater-shaker":
            assert slot, 'argument slot= is required when using "heater-shaker"'
            if slot in [1, 4, 7, 10]:
                side = "left"
            elif slot in [3, 6, 9, 12]:
                side = "right"
            else:
                raise ValueError("heater shaker must be on either left or right side")
            hw_offset = _hw_offsets[f"{item}-{side}"]
        else:
            hw_offset = _hw_offsets[item]
        if action == "pick-up":
            offset = hw_offset + _pick_up_offsets[item]
        else:
            offset = hw_offset + _drop_offsets[item]
        # convert from Point() to dict()
        return {"x": offset.x, "y": offset.y, "z": offset.z}

    def transfer(vol1, start, end, reagent=0):
        for i in range(NUM_COL):
                if reagent==1: p1000.pick_up_tip(tips_elu_loc[i*8])
                else: p1000.pick_up_tip(tips_reused_loc[i*8])
                start_loc = start[i]
                end_loc = end[i]
                if reagent==2: p1000.mix(5, vol1*0.75, start_loc.bottom(z=ASP_HEIGHT*2), rate = 2)
                p1000.aspirate(vol1, start_loc.bottom(z=ASP_HEIGHT), rate = 2)
                p1000.air_gap(10)
                p1000.dispense(vol1+10, end_loc.top(z=-5), rate = 2)
                p1000.blow_out()
                p1000.return_tip()
            
    def mix(speend, time):
        ctx.comment('\n\n\n~~~~~~~~Shake to mix~~~~~~~~\n')
        h_s.set_and_wait_for_shake_speed(rpm=speend)
        ctx.delay(seconds=time)
        h_s.deactivate_shaker()

    def discard(vol2, start):
        global waste_vol
        waste_vol = 0   
        for j in range(NUM_COL):  
            p1000.pick_up_tip(tips_reused_loc[j*8])  
            start_loc = start[j]
            end_loc = waste
            p1000.aspirate(vol2, start_loc.bottom(z=ASP_HEIGHT), rate = 0.3)
            p1000.air_gap(10)
            p1000.dispense(vol2+10, end_loc.top(z=5), rate = 2)
            p1000.blow_out()
            p1000.return_tip()
        waste_vol = vol2 * NUM_COL * 8
        
    # protocol

    waste_vol_chk = 0

    ## Equilibration
    h_s.open_labware_latch()
    ctx.pause('Move the Working Plate to the Shaker')
    h_s.close_labware_latch()

    if BEADS_PRELOAD == 0: transfer(BEADS_VOL, beads, working_cols, 2)
    transfer(EQUILIBRATION_VOL1, eql, working_cols)
    mix(MIX_SPEEND, MIX_SEC)

    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Magnet')
    ctx.move_labware(working_plate,
                     MAG_PLATE_SLOT,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","heater-shaker", 1),
                     drop_offset=grip_offset("drop","mag-plate")
                     )
    h_s.close_labware_latch()
    ctx.delay(minutes=MAG_DELAY_MIN)
    discard(EQUILIBRATION_VOL1*1.1+BEADS_VOL, working_cols)
    waste_vol_chk = waste_vol_chk + waste_vol
    if waste_vol_chk >= WASTE_VOL_MAX: 
        ctx.pause('Empty Liquid Waste')
        waste_vol_chk = 0

    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Shaker')
    ctx.move_labware(working_plate,
                     h_s,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","mag-plate"),
                     drop_offset=grip_offset("drop","heater-shaker", 1)
                     )
    h_s.close_labware_latch()

    transfer(EQUILIBRATION_VOL2, eql, working_cols)
    mix(MIX_SPEEND, MIX_SEC)

    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Magnet')
    ctx.move_labware(working_plate,
                     MAG_PLATE_SLOT,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","heater-shaker", 1),
                     drop_offset=grip_offset("drop","mag-plate")
                     )
    h_s.close_labware_latch()
    ctx.delay(minutes=MAG_DELAY_MIN)
    discard(EQUILIBRATION_VOL2*1.1, working_cols)
    waste_vol_chk = waste_vol_chk + waste_vol
    if waste_vol_chk >= WASTE_VOL_MAX: 
        ctx.pause('Empty Liquid Waste')
        waste_vol_chk = 0

    ## Protein Capture
    h_s.open_labware_latch()
    #ctx.pause('Move the Working Plate to the Shaker')
    ctx.move_labware(working_plate,
                     h_s,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","mag-plate"),
                     drop_offset=grip_offset("drop","heater-shaker", 1)
                     )
    h_s.close_labware_latch()

    transfer(SAMPLE_VOL, samples, working_cols)
    h_s.set_and_wait_for_shake_speed(rpm=MIX_SPEEND)
    ctx.delay(seconds=MIX_SEC)

    if INCUBATION_ON_DECK == 1:
        mix(INCUBATION_SPEEND, INCUBATION_MIN*60)
        h_s.open_labware_latch()

    else:
        # incubation off deck 
        h_s.deactivate_shaker()
        h_s.open_labware_latch()
        ctx.pause('Seal the Plate')
        ctx.pause('Remove the Seal, Move the Plate back to Shaker')
 
    #ctx.pause('Move the Working Plate to the Magnet')
    ctx.move_labware(working_plate,
                    MAG_PLATE_SLOT,
                    use_gripper=USE_GRIPPER,
                    pick_up_offset=grip_offset("pick-up","heater-shaker", 1),
                    drop_offset=grip_offset("drop","mag-plate")
                    )
    h_s.close_labware_latch()

    ctx.delay(minutes=MAG_DELAY_MIN)
    discard(SAMPLE_VOL*1.1, working_cols)
    waste_vol_chk = waste_vol_chk + waste_vol
    if waste_vol_chk >= WASTE_VOL_MAX: 
        ctx.pause('Empty Liquid Waste')
        waste_vol_chk = 0


    ## Wash
    for _ in range(WASH_TIMES):
        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Shaker')
        ctx.move_labware(working_plate,
                     h_s,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","mag-plate"),
                     drop_offset=grip_offset("drop","heater-shaker", 1)
                     )
        h_s.close_labware_latch()

        transfer(WASH_VOL, wash, working_cols)
        mix(MIX_SPEEND, MIX_SEC)

        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Magnet')
        ctx.move_labware(working_plate,
                     MAG_PLATE_SLOT,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","heater-shaker", 1),
                     drop_offset=grip_offset("drop","mag-plate")
                     )
        h_s.close_labware_latch()
        ctx.delay(minutes=MAG_DELAY_MIN)
        discard(WASH_VOL*1.1, working_cols)
        waste_vol_chk = waste_vol_chk + waste_vol
        if waste_vol_chk >= WASTE_VOL_MAX: 
            ctx.pause('Empty Liquid Waste')
            waste_vol_chk = 0

    ## Elution
    for j in range(ELUTION_TIMES):  
        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Shaker')
        ctx.move_labware(working_plate,
                     h_s,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","mag-plate"),
                     drop_offset=grip_offset("drop","heater-shaker", 1)
                     )
        h_s.close_labware_latch()

        transfer(ELUTION_VOL, elu, working_cols, 1)
        h_s.set_and_wait_for_shake_speed(rpm=MIX_SPEEND)
        ctx.delay(seconds=MIX_SEC)
        h_s.set_and_wait_for_shake_speed(rpm=ELUTION_SPEEND)
        if j == 0:
            temp.set_temperature(4)
            delay = ELUTION_MIN - COOLING_DELAY_MIN
            ctx.delay(seconds=delay*60)
        else:
            delay = ELUTION_MIN
            ctx.delay(seconds=delay*60)
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        #ctx.pause('Move the Working Plate to the Magnet')
        ctx.move_labware(working_plate,
                     MAG_PLATE_SLOT,
                     use_gripper=USE_GRIPPER,
                     pick_up_offset=grip_offset("pick-up","heater-shaker", 1),
                     drop_offset=grip_offset("drop","mag-plate")
                     )
        h_s.close_labware_latch()
        ctx.delay(minutes=MAG_DELAY_MIN)
        transfer(ELUTION_VOL*1.1, working_cols, final_cols, 1)
    
    ctx.pause('Protocol Complete')
    temp.deactivate()
