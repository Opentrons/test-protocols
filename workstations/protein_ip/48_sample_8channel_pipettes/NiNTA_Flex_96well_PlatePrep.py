from opentrons.types import Point

metadata = {
    'protocolName': 'Immobilized Metal Affinity Chromatography by Ni-NTA Magnetic Agarose Beads (plate preparation) - 96-well setting on Opentrons Flex',
    'author': 'Boren Lin, Opentrons',
    'description': 'This protocol prepares reagent plates for automated immobilized metal affinity chromatography (IMAC) using Ni-NTA magnetic agarose beads (up to 96 samples).'
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.15",
}

########################

NUM_COL = 12

ASP_HEIGHT = 0.2
BEADS_VOL = 100
EQUILIBRATION_VOL1 = 400
EQUILIBRATION_VOL2 = 500
SAMPLE_VOL = 500
WASH_TIMES = 2
WASH_VOL = 500
ELUTION_TIMES = 1
ELUTION_VOL = 250

#########################

def run(ctx):

    # load labware

    eql_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 8, 'equilibration buffer')
    wash_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 6, 'wash buffer')
    elution_res = ctx.load_labware('nest_96_wellplate_2ml_deep', 11, 'elution buffer')

    eql_stock = ctx.load_labware('nest_1_reservoir_195ml', 7, 'equilibration buffer')
    wash_stock = ctx.load_labware('nest_1_reservoir_195ml', 9, 'wash buffer')
    elution_stock = ctx.load_labware('nest_1_reservoir_195ml', 10, 'elution buffer')
   
    beads_stock = ctx.load_labware('nest_12_reservoir_15ml', 2, 'beads')
    h_s = ctx.load_module('heaterShakerModuleV1',1)
    h_s_adapter = h_s.load_adapter('opentrons_96_deep_well_adapter')
    working_plate = h_s_adapter.load_labware('nest_96_wellplate_2ml_deep', 'working plate')
    temp = ctx.load_module('Temperature Module Gen2', 3)

    tips = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', 5)
    p1000 = ctx.load_instrument('p1000_multi_gen3', 'left', tip_racks=[tips]) 

    # liquids
    eql = eql_res.rows()[0][:NUM_COL]
    wash = wash_res.rows()[0][:NUM_COL]
    elu = elution_res.rows()[0][:NUM_COL] # reagent 1

    eql_source = eql_stock.wells()[0]
    wash_source = wash_stock.wells()[0]
    elu_source = elution_stock.wells()[0]

    beads = beads_stock.wells()[0:2]
    working_cols = working_plate.rows()[0][:NUM_COL]

    def transfer_beads(vol, end):
        if NUM_COL <= 6:
            start = beads[0]
            p1000.pick_up_tip()
            p1000.mix(5, vol*NUM_COL*0.5, start.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.mix(5, vol*NUM_COL*0.5, start.bottom(z=ASP_HEIGHT*2), rate =2)
            p1000.aspirate(vol*NUM_COL, start.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.air_gap(10)
            end_loc = end[0]
            p1000.dispense(10, end_loc.top(z=0), rate = 0.75)
            for i in range(NUM_COL):
                end_loc = end[i]
                p1000.dispense(vol, end_loc.top(z=-5), rate = 0.75)  
            p1000.blow_out()      
            p1000.drop_tip()
        else:
            start1 = beads[0]
            p1000.pick_up_tip()
            p1000.mix(5, vol*6*0.5, start1.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.mix(5, vol*6*0.5, start1.bottom(z=ASP_HEIGHT*2), rate = 2)
            p1000.aspirate(vol*6, start1.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.air_gap(10)
            end_loc = end[0]
            p1000.dispense(10, end_loc.top(z=0), rate = 0.75)
            for i in range(6):
                end_loc = end[i]
                p1000.dispense(vol, end_loc.top(z=-5), rate = 0.75)   
            p1000.blow_out() 

            cols = NUM_COL - 6

            start2 = beads[1]
            p1000.mix(5, vol*cols*0.5, start2.bottom(z=ASP_HEIGHT), rate = 2)
            p1000.mix(5, vol*cols*0.5, start2.bottom(z=ASP_HEIGHT*2), rate = 2)
            p1000.aspirate(vol*cols, start2.bottom(z=ASP_HEIGHT), rate =2)
            p1000.air_gap(10)
            end_loc = end[6]
            p1000.dispense(10, end_loc.top(z=0), rate =0.75)
            for j in range(cols):
                end_loc = end[j+6]
                p1000.dispense(vol, end_loc.top(z=-5), rate = 0.75)   
            p1000.blow_out() 
            p1000.drop_tip()            

    def transfer_buffer(vol, start, end):
        if vol > 800:
            n = int(vol//800)
            if vol%800 != 0: n = n + 1
            p1000.pick_up_tip()
            for _ in range(n):
                for j in range(NUM_COL):
                    start_loc = start.bottom(z=ASP_HEIGHT).move(Point(x=j*9-49.5))
                    end_loc = end[j]
                    p1000.aspirate(vol/n, start_loc, rate = 2)
                    p1000.air_gap(10)
                    p1000.dispense(vol+10, end_loc.top(z=-5), rate =2)        
            p1000.drop_tip()
        else:
            p1000.pick_up_tip()
            for j in range(NUM_COL):
                start_loc = start.bottom(z=ASP_HEIGHT).move(Point(x=j*9-49.5))
                end_loc = end[j]
                p1000.aspirate(vol, start_loc, rate = 2)
                p1000.air_gap(10)
                p1000.dispense(vol+10, end_loc.top(z=-5), rate =2)        
            p1000.drop_tip()

    # protocol

    ## working plate w/ beads
    h_s.open_labware_latch()
    ctx.pause('Move the Working Plate to the Shaker')
    h_s.close_labware_latch()
    transfer_beads(BEADS_VOL, working_cols)
    h_s.open_labware_latch()

    ## wash buffer
    transfer_buffer(WASH_VOL*WASH_TIMES+50, wash_source, wash)
    ## equilibration buffer
    transfer_buffer(EQUILIBRATION_VOL1+EQUILIBRATION_VOL2+50, eql_source, eql)  
    ## elution buffer
    transfer_buffer(ELUTION_VOL*ELUTION_TIMES+50, elu_source, elu)

    