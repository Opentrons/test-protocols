from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'HDQ_DNA_Bacteria Liquid Run Set Up - NOT DONE',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

res_type="nest_12_reservoir_15ml"
deepwell_type = "nest_96_wellplate_2ml_deep"
num_samples = 48


def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    tiprack_1000a       = protocol.load_labware(load_name ='opentrons_flex_96_tiprack_1000ul', location ='D1') # Tip Rack
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000a]) # Pipette
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')

    res1                = protocol.load_labware(res_type, 'D2', 'reagent reservoir 1')
    res2                = protocol.load_labware(res_type, 'D3', 'reagent reservoir 2')
    sample_plate        = protocol.load_labware(deepwell_type, 'C3')
    elution_plate       = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', 'B3')

    # Label Reservoirs
    binding_buffer  = res1.wells()[:2]
    elution_one     = res1.wells()[10:]
    wash1a          = res2['A1'].top()
    wash1b          = res2['A2'].top()
    wash1c          = res2['A3'].top()
    wash2a          = res2['A4'].top()
    wash2b          = res2['A5'].top()
    wash2c          = res2['A6'].top()
    wash3a          = res2['A7'].top()
    wash3b          = res2['A8'].top()
    wash3c          = res2['A9'].top()
    AL              = res1['A1'].top()
    TLa             = res1['A3'].top()
    TLb             = res1['A4'].top()
    TLc             = res1['A5'].top()
    
    # Label Sample and Elution Plate
    samples_m = sample_plate.rows()[0][:6]
    TL_samples_m = sample_plate.rows()[0][6:2*6]
    elution_samples_m = elution_plate.rows()[0][:6]
    
    # Res 1
    p1000.distribute(volume = [binding_buffer_vol, AL_vol, TL_vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [binding_buffer, AL, TL], trash = False)
    
    # Res2
    p1000.distribute(volume = [wash1_vol, wash1_vol, wash1_vol, wash2_vol, wash2_vol, wash2_vol, wash3_vol, wash3_vol, wash3_vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [wash1a, wash1b, wash1c, wash2a, wash2b, wash2c, wash3a, wash3b, wash3c], trash = False)
    
    # Sample Plate
    p1000.distribute(volume = [sample_vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [sample_plate], trash = False)
    
    # Elution Samples
    p1000.distribute(volume = [elution_vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [elution_plate], trash = False)