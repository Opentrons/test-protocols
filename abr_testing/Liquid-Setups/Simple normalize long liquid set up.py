from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'DVT1ABR1: Simple Normalize Long Liquid Set Up',
    'author': 'Rhyann clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.16",
}

# Weigh plates before and after run

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    trash_bin           = protocol.load_trash_bin("A3")
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    reservoir           = protocol.load_labware('nest_12_reservoir_15ml','D2', 'Reservoir') # Reservoir
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000]) # Pipette

    vol = 5400 / 8
    
    columns = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
    for i in columns:
        p1000.transfer(vol, source = master_reservoir['A1'].bottom(z=0.5), dest = reservoir[i].top(), blowout = True, blowout_location = 'source well', trash = False)