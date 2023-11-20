from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Illumina DNA Enrichment v4 Evaporation Test',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

def run(protocol: protocol_api.ProtocolContext):
    
    global p200_tips
    global p50_tips
    
    # DECK SETUP AND LABWARE
    # ========== FIRST ROW ===========
    heatershaker        = protocol.load_module('heaterShakerModuleV1','1')

    ####### METHOD ONE FOR ADAPTER AND LABWARE SEPERATE #############
    hs_adapter          = heatershaker.load_adapter("opentrons_96_deep_well_adapter")
    sample_plate_2      = hs_adapter.load_labware("nest_96_wellplate_2ml_deep")

    ####### METHOD TWO FOR ADAPTER AND LABWARE TOGETHER #############
    # sample_plate_2      = heatershaker.load_labware('nest_96_wellplate_2ml_deep', adapter = 'opentrons_96_deep_well_adapter')
    # hs_adapter          = sample_plate_2.parent

    tiprack_200_1       = protocol.load_labware('opentrons_flex_96_tiprack_200ul', '2')
    temp_block          = protocol.load_module('temperature module gen2', '3')
    temp_block_adapter  = temp_block.load_adapter('opentrons_96_well_aluminum_block')
    reagent_plate       = temp_block_adapter.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    # ========== SECOND ROW ==========
    MAG_PLATE_SLOT      = protocol.load_module('magneticBlockV1', '4')
    reservoir           = protocol.load_labware('nest_12_reservoir_15ml','5')    
    tiprack_200_2       = protocol.load_labware('opentrons_flex_96_tiprack_200ul', '6')
    # ========== THIRD ROW ===========
    thermocycler        = protocol.load_module('thermocycler module gen2')
    sample_plate_1      = thermocycler.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    tiprack_20          = protocol.load_labware('opentrons_flex_96_tiprack_50ul', '9')
    
    # pipette
    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_200_1,tiprack_200_2])
    p50 = protocol.load_instrument("flex_8channel_50", "right", tip_racks=[tiprack_20])


    #-weigh empty Armadillo-
    # set thermocycler block to 4°, lid to 105°
    thermocycler.open_lid()
    thermocycler.set_block_temperature(4)
    thermocycler.set_lid_temperature(105)
    #pipette 10uL into Armadillo wells
    locations = [sample_plate_1['A1'].bottom(z=0.5),
            sample_plate_1['A2'].bottom(z=0.5),
            sample_plate_1['A3'].bottom(z=0.5),
            sample_plate_1['A4'].bottom(z=0.5),
            sample_plate_1['A5'].bottom(z=0.5),
            sample_plate_1['A6'].bottom(z=0.5),
            sample_plate_1['A7'].bottom(z=0.5),
            sample_plate_1['A8'].bottom(z=0.5),
            sample_plate_1['A9'].bottom(z=0.5),
            sample_plate_1['A10'].bottom(z=0.5),
            sample_plate_1['A11'].bottom(z=0.5),
            sample_plate_1['A12'].bottom(z=0.5)]
    volumes = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    protocol.pause('Weight Armadillo Plate, place on thermocycler')
    p50.distribute(volume = volumes, source = reservoir['A1'].bottom(z=0.4), dest = locations, return_tips = True, blow_out = False)
    #-weigh filled Armadillo, place onto thermocycler-
    protocol.pause('Weight Armadillo Plate, place on thermocycler')
    #Close lid
    thermocycler.close_lid()
    #hold at 95° for 3 minutes
    profile_TAG = [{'temperature': 95, 'hold_time_minutes': 3}]
    thermocycler.execute_profile(steps = profile_TAG, repetitions = 1)
    #30x cycles of: 70° for 30s 72° for 30s 95° for 10s 
    profile_TAG2 = [{'temperature': 70, 'hold_time_seconds': 30}, {'temperature': 72, 'hold_time_seconds': 0.5}, {'temperature': 95, 'hold_time_seconds': 10}]
    thermocycler.execute_profile(steps = profile_TAG2, repetitions = 30)
    #hold at 72° for 5min 
    profile_TAG3 = [{'temperature': 72, 'hold_time_minutes': 5}]
    thermocycler.execute_profile(steps = profile_TAG3, repetitions = 1)
    # # Cool to 4° 
    thermocycler.set_block_temperature(4)
    thermocycler.set_lid_temperature(105)
    # Open lid
    thermocycler.open_lid()
    protocol.pause('Weigh Armadillo plate')