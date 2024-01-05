from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Pick Up 50 uL Tips',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE 
    reservoir_12well    = protocol.load_labware('nest_12_reservoir_15ml', location = 'D1')
    reagent_plate       = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', location = 'D2')
    reservoir_96well    = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'D3') 
    
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C1')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C2')
    tiprack_50_3        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C3')
    
    # ========== THIRD ROW ===========
    thermocycler        = protocol.load_module('thermocycler module gen2')

    # pipette

    p50 = protocol.load_instrument("flex_8channel_50", "left", tip_racks=[tiprack_50_1,tiprack_50_2, tiprack_50_3])
    
    column_list   = ['A1','A2','A3','A4','A5','A6', 'A7','A8','A9','A10','A11','A12']
    thermocycler.open_lid()
    
    for i in list(range(3)):
        for n in column_list:
            p50.pick_up_tip()
            p50.aspirate(30, reservoir_12well[n].bottom(z = 1))
            p50.dispense(10, reagent_plate[n].bottom(z = 0.5))
            p50.dispense(10, reservoir_96well[n].bottom(z = 0.5))
            p50.return_tip()
