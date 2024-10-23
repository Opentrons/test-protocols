from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'DVT1ABR4/8: Illumina DNA Prep v4.7 with tc auto seal lid Liquid Set Up',
    'author': 'Tony Ngumah <tony.ngumah@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.20",
}

# Protocol to fill sample plate, reagent plate, and reservoir for Illumina DNA Prep 24x v4.7 Liquid Set Up
# Weigh plates before and after run

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    trash_bin           = protocol.load_trash_bin("A3")
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')

    reservoir_1         = protocol.load_labware('nest_96_wellplate_2ml_deep','D2', 'Reservoir1') # Reservoir
    reservoir_2         = protocol.load_labware('thermoscientificnunc_96_wellplate_1300ul', 'D3', 'Reservoir2') # Reservoir
    sample_plate_1      = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt",'C3', 'Sample Plate') # Sample Plate
    reagent_plate_1     = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt",'B3', 'Reagent Plate') # reagent Plate
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000]) # Pipette
    
    # Reagent Plate Prep: dispense liquid into columns 4 - 7 - total 156 ul
    p1000.distribute(volume = [75, 15, 20, 65], source = master_reservoir['A1'].bottom(z=0.5), dest = [reagent_plate_1['A4'], reagent_plate_1['A5'], reagent_plate_1['A6'], reagent_plate_1['A7']], blow_out = True, blowout_location = 'source well', trash = False)
    
    # Reservoir 1 Plate Prep: dispense liquid into columns 1, 2, 4, 5 total 1866 ul
    p1000.transfer(volume = [120,750,900,96], source = master_reservoir['A1'], dest = [reservoir_1['A1'].top(), reservoir_1['A2'].top(), reservoir_1['A4'].top(), reservoir_1['A5'].top()], blow_out = True, blowout_location = 'source well', trash = False)

    # Reservoir 2 Plate Prep: dispense liquid into columns 1-9 total 3690 ul
    p1000.transfer(volume = [50,50,50,50,50,50,330,330,330,800,800,800], source = master_reservoir['A1'], dest = [reservoir_2['A1'].top(), reservoir_2['A2'].top(), reservoir_2['A3'].top(), reservoir_2['A4'].top(), reservoir_2['A5'].top(), reservoir_2['A6'].top(), reservoir_2['A7'].top(), reservoir_2['A8'].top(), reservoir_2['A9'].top(), reservoir_2['A10'].top(), reservoir_2['A11'].top(), reservoir_2['A12'].top()], blow_out = True, blowout_location = 'source well', trash = False)

    # Sample Plate Prep: total 303
    p1000.transfer(volume = [101, 101, 101], source = master_reservoir['A1'], dest = [sample_plate_1['A1'], sample_plate_1['A2'], sample_plate_1['A3']], blow_out = True, blowout_location = 'source well', trash = False)