from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'PVT1ABR7: HDQ_DNA_Bacteria Liquid Run Set Up',
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
    tiprack_1000a       = protocol.load_labware(load_name ='opentrons_flex_96_tiprack_1000ul', location ='D1') # Tip Rack
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000a]) # Pipette
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    sample_plate        = protocol.load_labware("nest_96_wellplate_2ml_deep", "C3", "Sample Plate")
    elution_plate       = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", "B3", "Elution Plate")
    res1                = protocol.load_labware(res_type, 'D2', 'reagent reservoir 1')

    # Label Reservoirs
    well1  = res1['A1'].top()
    well2  = res1['A2'].top()
    well3  = res1['A3'].top()
    well4  = res1['A4'].top()
    well5  = res1['A5'].top()
    well6  = res1['A6'].top()
    well7  = res1['A7'].top()
    well8  = res1['A8'].top()
    well9  = res1['A9'].top()
    well10  = res1['A10'].top()
    well11 = res1['A11'].top()
    well12  = res1['A12'].top()
    
    #Volumes
    wash = 600
    al_and_pk = 468
    beads_and_binding = 552
    
    # Sample Plate
    p1000.transfer(volume = 180, source = master_reservoir['A1'].bottom(z=0.5), dest =sample_plate["A1"].top(), blowout = True, blowout_location = 'source well', trash = False)
    # Elution Plate
    p1000.transfer(volume = 100, source = master_reservoir['A1'].bottom(z=0.5), dest = elution_plate["A1"].top(), blowout = True, blowout_location = 'source well', trash = False)
    # Res 1
    p1000.transfer(volume = [beads_and_binding,al_and_pk, wash, wash, wash], source = master_reservoir['A1'].bottom(z=0.5), dest = [well1, well3, well4, well7, well10], blowout = True, blowout_location = 'source well', trash = False)
    