from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'HDQ_DNA_Bacteria Liquid Run Set Up',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.16",
}

res_type="nest_12_reservoir_15ml"

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    waste_chute         = protocol.load_waste_chute()
    trash_bin           = protocol.load_trash_bin("A3")
    tiprack_1000a       = protocol.load_labware(load_name ='opentrons_flex_96_tiprack_1000ul', location ='D1') # Tip Rack
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000a]) # Pipette
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')

    res1                = protocol.load_labware(res_type, 'C3', 'reagent reservoir 1')
    res2                = protocol.load_labware(res_type, 'B3', 'reagent reservoir 2')

    # Label Reservoirs
    binding_buffer1  = res1['A1'].top()
    binding_buffer2  = res1['A2'].top()
    wash1a          = res2['A1'].top()
    wash1b          = res2['A2'].top()
    wash1c          = res2['A3'].top()
    wash2a          = res2['A4'].top()
    wash2b          = res2['A5'].top()
    wash2c          = res2['A6'].top()
    wash3a          = res2['A7'].top()
    wash3b          = res2['A8'].top()
    wash3c          = res2['A9'].top()
    AL              = res1['A3'].top()
    TLa             = res1['A4'].top()
    TLb             = res1['A5'].top()
    Elution1        = res1['A11'].top()
    Elution2        = res1['A12'].top()
    
    #Volumes
    binding_buffer_vol = 9280 / 8
    AL_vol = 12650 / 8
    TL_vol = (7500 + 600) / 8
    elution_vol = 10150 / 8
    wash1_vol = 11400 / 8
    wash2_vol = 11400 / 8
    wash3_vol = 11400/ 8
    # Res 1
    p1000.transfer(volume = [binding_buffer_vol, binding_buffer_vol, AL_vol, TL_vol, TL_vol, elution_vol, elution_vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [binding_buffer1, binding_buffer2, AL, TLa, TLb, Elution1, Elution2], blowout = True, blowout_location = 'source well', trash = False)
    
    # Res2
    p1000.transfer(volume = [wash1_vol, wash1_vol, wash1_vol, wash2_vol, wash2_vol, wash2_vol, wash3_vol, wash3_vol, wash3_vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [wash1a, wash1b, wash1c, wash2a, wash2b, wash2c, wash3a, wash3b, wash3c], blowout = True, blowout_location = 'source well', trash = False)
    
