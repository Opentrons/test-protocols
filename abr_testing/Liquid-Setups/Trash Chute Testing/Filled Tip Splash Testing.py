from opentrons import protocol_api
from opentrons import types

import random

metadata = {
    'protocolName': 'Throw out Liquid Filled Tips',
    'author': 'Rhyann clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
}
requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.16'
}

def run(protocol: protocol_api.ProtocolContext):
    waste_chute = protocol.load_waste_chute()
    
    # Initiate Labware
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000]) # Pipette

    p1000.pick_up_tip()
    p1000.aspirate(500, master_reservoir['A1'].bottom(z=0.5))
    p1000.drop_tip()