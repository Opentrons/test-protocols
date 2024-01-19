from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'ZymoBIOMICS Magbead Liquid Run Set Up',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.16",
}

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    waste_chute         = protocol.load_waste_chute()
    trash_bin           = protocol.load_trash_bin("A3")
    tiprack_1000a       = protocol.load_labware(load_name ='opentrons_flex_96_tiprack_1000ul', location ='D1') # Tip Rack
    tiprack_1000b       = protocol.load_labware(load_name ='opentrons_flex_96_tiprack_1000ul', location ='C1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    res1                = protocol.load_labware("nest_12_reservoir_15ml", 'C3', 'R1')
    res2                = protocol.load_labware("nest_12_reservoir_15ml", 'B3', 'R2')
    p1000               = protocol.load_instrument(instrument_name ='flex_8channel_1000', mount ='left', tip_racks = [tiprack_1000a, tiprack_1000b]) # Pipette
    
    # Reservoir 1: Well 1 - 12,320 ul, Wells 2-4 - 11,875 ul, Wells 5-6 - 13,500 ul, Wells 7-8 - 13,500 ul, Well 12 - 5,200 ul
    well1 = 12320 / 8
    well2_4 = 11875 / 8
    well5_6 = 13500 / 8
    well7_8 = 13500 / 8 
    well12 = 5200 / 8
    # Reservoir 2: Wells 1-12 - 9,000 ul
    res2_well = 9000 / 8
    # Fill up Plates
    # Res1
    p1000.distribute(volume = [well1, well2_4, well2_4, well2_4, well5_6, well5_6, well7_8, well7_8, well12], source = master_reservoir['A1'].bottom(z = 0.2), dest = [res1['A1'].top(),res1['A2'].top(), res1['A3'].top(), res1['A4'].top(), res1['A5'].top(), res1['A6'].top(), res1['A7'].top(), res1['A8'].top(), res1['A12'].top()], blow_out = True, blowout_location = 'source well', trash = False)
    # Res2
    p1000.distribute(volume = [res2_well, res2_well, res2_well, res2_well, res2_well, res2_well, res2_well, res2_well, res2_well, res2_well, res2_well, res2_well], source = master_reservoir['A1'], dest = [res2['A1'].top(), res2['A2'].top(),res2['A3'].top(), res2['A4'].top(), res2['A5'].top(), res2['A6'].top(), res2['A7'].top(), res2['A8'].top(), res2['A9'].top(), res2['A10'].top(), res2['A11'].top(), res2['A12'].top()], blow_out = True, blowout_location = 'source well', trash = False)