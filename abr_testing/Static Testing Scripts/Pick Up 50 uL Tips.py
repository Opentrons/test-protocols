from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Pick Up 50 uL Tips Right and Left - 5 racks',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE     
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'A2')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'B2')
    tiprack_50_3        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C2')
    tiprack_50_4        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'B3')
    tiprack_50_5        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', location = 'C3')

    # Pipette
    p50 = protocol.load_instrument("flex_8channel_50", "right", tip_racks=[tiprack_50_1,tiprack_50_2, tiprack_50_3, tiprack_50_4, tiprack_50_5])
    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_50_1,tiprack_50_2, tiprack_50_3, tiprack_50_4, tiprack_50_5])
    
    for i in list(range(4)):
        for i in list(range(60)):
            p50.pick_up_tip()
            p50.return_tip()
        p50.reset_tipracks()
        for i in list(range(60)):
            p1000.pick_up_tip()
            p1000.return_tip()
        p1000.reset_tipracks()