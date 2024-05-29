# Liquid Set up

from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Trash Chute Liquid Run Set Up - 96 Deep 2ml well',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    tiprack_1000a       = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    #pcr_plate           = protocol.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt', location = 'D2')
    #pcr_plate2          = protocol.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt', location = 'D3')
    res1                = protocol.load_labware(load_name= 'nest_96_wellplate_2ml_deep', location= 'D2')
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000a, tiprack_1000b]) # Pipette
    
    vol = 400
    columns =['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
    p1000.distribute(volume = [vol, vol, vol, vol, vol, vol, vol, vol, vol, vol, vol, vol], source = master_reservoir['A1'].bottom(z = 0.2), dest = [res1['A1'].top(),res1['A2'].top(), res1['A3'].top(), res1['A4'].top(), res1['A5'].top(), res1['A6'].top(), res1['A7'].top(), res1['A8'].top(), res1['A9'].top(), res1['A10'].top(), res1['A11'].top(), res1['A12'].top()], blow_out = True, blowout_location = 'source well')

    