from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Tip Pick Test 200 ul Left mount',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE 
    reservoir_96well    = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'D3') 
    reservoir_12well    = protocol.load_labware('nest_12_reservoir_15ml', location = 'D1')
    reagent_plate       = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', location = 'D2')
    
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_200ul', location = 'C2')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_200ul', location = 'B2')
    tiprack_50_3        = protocol.load_labware('opentrons_flex_96_tiprack_200ul', location = 'A2')
    
    # ========== THIRD ROW ===========
    thermocycler        = protocol.load_module('thermocycler module gen2')

    # pipette

    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_50_1,tiprack_50_2, tiprack_50_3])
    
    column_list   = ['A1','A2','A3','A4','A5','A6', 'A7','A8','A9','A10','A11','A12']
    thermocycler.open_lid()
    
    for i in list(range(6)):
        for i in list(range(36)):
            p1000.pick_up_tip()
            p1000.return_tip()
        p1000.reset_tipracks()
