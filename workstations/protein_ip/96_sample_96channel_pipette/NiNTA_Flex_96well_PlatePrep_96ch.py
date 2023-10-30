metadata = {
    'protocolName': 'Immobilized Metal Affinity Chromatography by Ni-NTA Magnetic Agarose Beads (plate preparation) - 96-well setting on Opentrons Flex with 96 channel pipette',
    'author': 'Boren Lin, Opentrons',
    'description': 'This protocol prepares reagent plates for automated immobilized metal affinity chromatography (IMAC) using Ni-NTA magnetic agarose beads (up to 96 samples).'
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

########################

NUM_SAMPLES = 96

ASP_HEIGHT = 0.6
BEADS_VOL = 100
EQUILIBRATION_VOL1 = 400
EQUILIBRATION_VOL2 = 500
SAMPLE_VOL = 500
WASH_TIMES = 2
WASH_VOL = 500
ELUTION_TIMES = 2
ELUTION_VOL = 250

BEADS_PRELOAD = 0
# NO: 0; YES: 1

TIPS_REUSE = 1
# NO: 0; YES:1

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

    eql_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B2', 'equilibration buffer')
    wash_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 'C3', 'wash buffer')
    elution_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 'A2', 'elution buffer')
    
    eql_stock = ctx.load_labware('nest_1_reservoir_290ml', 'B1', 'equilibration stock')
    wash_stock = ctx.load_labware('nest_1_reservoir_290ml', 'B3', 'wash stock')
    elution_stock = ctx.load_labware('nest_1_reservoir_290ml', 'A1', 'elution stock')

    if BEADS_PRELOAD == 1: 
        beads_stock = ctx.load_labware('nest_1_reservoir_290ml', 'C1', 'beads')
        h_s = ctx.load_module('heaterShakerModuleV1', 'D1')
        h_s_adapter = h_s.load_adapter('opentrons_96_deep_well_adapter')
        working_plate = h_s_adapter.load_labware("nest_96_wellplate_2ml_deep", 'wokring plate')

    temp = ctx.load_module('Temperature Module Gen2', 'D3')

    tips = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'D2', adapter='opentrons_flex_96_tiprack_adapter')
    p1000 = ctx.load_instrument('flex_96channel_1000', 'left', tip_racks=[tips]) 


    # liquids
    eql = eql_res.wells()[:NUM_SAMPLES]
    wash = wash_res.wells()[:NUM_SAMPLES]
    elution = elution_res.wells()[:NUM_SAMPLES]

    eql_source = eql_stock.wells()[0]
    wash_source = wash_stock.wells()[0]
    elution_source = elution_stock.wells()[0]

    if BEADS_PRELOAD == 1: 
        beads_start = beads_stock.wells()[0]
        beads_end = working_plate.wells()[:NUM_SAMPLES]

    def transfer_buffer(vol, start, end):
        ctx.pause('Load Tips')
        p1000.reset_tipracks() 
        p1000.pick_up_tip()
        vol = vol + 100
        n = int(vol//750)
        if vol%750 != 0: n = n + 1
        for _ in range(n):        
            end_loc = end[0]
            p1000.aspirate(vol/n, start.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.air_gap(10)
            p1000.dispense(vol/n+10, end_loc.top(z=-5), rate = 2)     
            p1000.blow_out() 
        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip() 

    def transfer_buffer_reusetips(vol, start, end):
        vol = vol + 100
        n = int(vol//750)
        if vol%750 != 0: n = n + 1
        for _ in range(n):        
            end_loc = end[0]
            p1000.aspirate(vol/n, start.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.air_gap(10)
            p1000.dispense(vol/n+10, end_loc.top(z=-5), rate = 2)     
            p1000.blow_out() 
            
    # protocol

    if BEADS_PRELOAD == 1:
        h_s.open_labware_latch()
        ctx.pause('Move the Working Plate to the Shaker')
        h_s.close_labware_latch()

    if TIPS_REUSE == 0: 
        ## equilibration buffer
        transfer_buffer(EQUILIBRATION_VOL1 + EQUILIBRATION_VOL2, eql_source, eql)
        ## wash buffer
        transfer_buffer(WASH_VOL * WASH_TIMES, wash_source, wash)
        ## elution buffer
        transfer_buffer(ELUTION_VOL * ELUTION_TIMES, elution_source, elution)
        ## working plate w/ beads 
        if BEADS_PRELOAD == 1:
            ctx.pause('Load Tips')
            p1000.reset_tipracks() 
            p1000.pick_up_tip()
            end_loc = beads_end[0]
            p1000.mix(10, BEADS_VOL*0.75, beads_start.bottom(z=ASP_HEIGHT), rate = 2)    
            p1000.aspirate(BEADS_VOL, beads_start.bottom(z=ASP_HEIGHT), rate = 0.5)
            p1000.air_gap(10)
            p1000.dispense(10, end_loc.top(z=-5), rate = 2)
            p1000.dispense(BEADS_VOL, end_loc.bottom(z=7.5), rate = 1)     
            p1000.blow_out()
            p1000.return_tip if TIP_TRASH == False else p1000.drop_tip()

            h_s.open_labware_latch()

    else:
        p1000.pick_up_tip()
        ## equilibration buffer
        transfer_buffer_reusetips(EQUILIBRATION_VOL1 + EQUILIBRATION_VOL2, eql_source, eql)
        ## wash buffer
        transfer_buffer_reusetips(WASH_VOL * WASH_TIMES, wash_source, wash)
        ## elution buffer
        transfer_buffer_reusetips(ELUTION_VOL * ELUTION_TIMES, elution_source, elution)
        ## working plate w/ beads 
        if BEADS_PRELOAD == 1:
            end_loc = beads_end[0]
            p1000.mix(10, BEADS_VOL*0.75, beads_start.bottom(z=ASP_HEIGHT), rate = 2)    
            p1000.aspirate(BEADS_VOL, beads_start.bottom(z=ASP_HEIGHT), rate = 0.5)
            p1000.air_gap(10)
            p1000.dispense(10, end_loc.top(z=-5), rate = 2)
            p1000.dispense(BEADS_VOL, end_loc.bottom(z=7.5), rate = 1)     
            p1000.blow_out()

            h_s.open_labware_latch()
        
        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()