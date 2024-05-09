from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'PVT1ABR9: Thermo MagMax RNA Extraction Liquid Run Set Up',
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
    tiprack_1000a       = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    tiprack_1000b       = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='C1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    res1                = protocol.load_labware('nest_12_reservoir_15ml', 'D2', 'Reservoir') # Reservoir
    elution_plate       = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 'C3', 'Elution Plate')
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000a, tiprack_1000b]) # Pipette
    sample_plate        = protocol.load_labware('nest_96_wellplate_2ml_deep', 'B3', 'Sample Plate')
    
    num_samples = 48
    elution_vol = 55
    well1 = 8120/8
    well2 = 6400/8
    well3_7 = 8550/8
    sample_vol = 60
    
    # Reservoir
    p1000.distribute(volume = [well1, well2, well3_7, well3_7, well3_7, well3_7, well3_7], source = master_reservoir['A1'].bottom(z = 0.2), dest = [res1['A1'].top(), res1['A2'].top(), res1['A3'].top(), res1['A4'].top(), res1['A5'].top(), res1['A6'].top(), res1['A7'].top()], blow_out = True, blowout_location = 'source well', trash = False)
    # Elution Plate
    p1000.distribute(volume = [elution_vol, elution_vol, elution_vol,elution_vol, elution_vol, elution_vol,elution_vol, elution_vol, elution_vol,elution_vol, elution_vol, elution_vol], source = master_reservoir['A1'].bottom(z = 0.2), dest = [elution_plate['A1'].bottom(z=0.3), elution_plate['A2'].bottom(z=0.3), elution_plate['A3'].bottom(z=0.3), elution_plate['A4'].bottom(z=0.3), elution_plate['A5'].bottom(z=0.3), elution_plate['A6'].bottom(z=0.3),elution_plate['A7'].bottom(z=0.3), elution_plate['A8'].bottom(z=0.3), elution_plate['A9'].bottom(z=0.3), elution_plate['A10'].bottom(z=0.3), elution_plate['A11'].bottom(z=0.3), elution_plate['A12'].bottom(z=0.3)], blow_out = True, blowout_location = 'source well', trash = False)
    # Sample Plate
    p1000.distribute(volume = [sample_vol, sample_vol, sample_vol, sample_vol, sample_vol, sample_vol], source = master_reservoir['A1'].bottom(z = 0.2), dest = [sample_plate['A7'].top(), sample_plate['A8'].top(), sample_plate['A9'].top(), sample_plate['A10'].top(), sample_plate['A11'].top(), sample_plate['A12'].top()], blow_out = True, blowout_location = 'source well', trash = False)
    