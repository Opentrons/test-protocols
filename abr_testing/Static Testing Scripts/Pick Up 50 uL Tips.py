from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Pick Up 50 uL Tips Right and Left',
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
    
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C2')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'B2')
    tiprack_50_3        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'A2')
    tiprack_50_4        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C3')
    tiprack_50_5        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'B3')
    
    
    # ========== THIRD ROW ===========
    thermocycler        = protocol.load_module('thermocycler module gen2')

    # pipette
    p50 = protocol.load_instrument("flex_8channel_50", "right", tip_racks=[tiprack_50_1,tiprack_50_2, tiprack_50_3])
    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_50_1,tiprack_50_2, tiprack_50_3])
    
    column_list   = ['A1','A2','A3','A4','A5','A6', 'A7','A8','A9','A10','A11','A12']
    thermocycler.open_lid()
    for i in list(range(3)):
        for n in column_list:
            p50.pick_up_tip()
            p50.aspirate(30, reservoir_12well[n].bottom(z = 1))
            p50.dispense(10, reagent_plate[n].bottom(z = 0.5))
            p50.dispense(10, reservoir_96well[n].bottom(z = 0.5))
            p50.return_tip()
    p50.reset_tipracks()
    for i in list(range(3)):
        for n in column_list:
            p1000.pick_up_tip()
            p1000.aspirate(30, reservoir_12well[n].bottom(z = 1))
            p1000.dispense(10, reagent_plate[n].bottom(z = 0.5))
            p1000.dispense(10, reservoir_96well[n].bottom(z = 0.5))
            p1000.return_tip()