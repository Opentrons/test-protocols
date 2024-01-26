from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Tip Pick Test 200 ul Left mount - first and last column',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE 
    reagent_plate       = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'D2')
    temp_block          = protocol.load_module('temperature module gen2', '3')
    pcr_plate       = temp_block.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_200ul', location = 'C2')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_200ul', location = 'B2')
    tiprack_50_3        = protocol.load_labware('opentrons_flex_96_tiprack_200ul', location = 'A2')
    
    # ========== THIRD ROW ===========
    thermocycler        = protocol.load_module('thermocycler module gen2')

    # pipette

    tips = [tiprack_50_1,tiprack_50_2, tiprack_50_3]
    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks= tips)
    
    thermocycler.open_lid()
    
    for i in tips:
        p1000.pick_up_tip(i['A1'])
        p1000.aspirate(10, reagent_plate['A1'])
        p1000.dispense(10, pcr_plate['A1'])
        p1000.return_tip()
        
        p1000.pick_up_tip(i['A12'])
        p1000.aspirate(10, reagent_plate['A1'])
        p1000.dispense(10, pcr_plate['A1'])
        p1000.return_tip()
        
