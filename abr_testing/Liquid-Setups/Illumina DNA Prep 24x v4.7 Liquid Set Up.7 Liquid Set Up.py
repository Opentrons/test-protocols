from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Illumina DNA Prep 24x v4.7 Liquid Set Up',
    'author': 'Rhyann clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

# Protocol to fill sample plate, reagent plate, and reservoir for Illumina DNA Prep 24x v4.7 Liquid Set Up
# Weigh plates before and after run

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    reservoir           = protocol.load_labware('nest_12_reservoir_15ml','D2') # Reservoir
    sample_plate_1      = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt",'D3') # Sample Plate
    reagent_plate_1     = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt",'C3') # reagent Plate
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000]) # Pipette
    
    # Sample Plate Prep: dispense 30 ul into columns 1 - 4 - total 960 ul
    p1000.distribute(volume = [30, 30, 30, 30], source = master_reservoir['A1'].bottom(z=0.5), dest = [sample_plate_1['A1'], sample_plate_1['A2'], sample_plate_1['A3'], sample_plate_1['A4']], blow_out = True)
    
    # Reservoir Plate Prep: dispense 375, 250, 900, 900 uls into columns 1, 2, 4, and 6 - total 19400 ul
    p1000.transfer(volume = [375, 250, 900, 900], source = master_reservoir['A1'], dest = [reservoir['A1'].top(), reservoir['A2'].top(), reservoir['A4'].top(), reservoir['A6'].top()], blow_out = True)

    # Reagent Plate Prep: 66, 132, 120, 96, 5, 5, 5, 5 - total 3472 
    p1000.transfer(volume = [66, 132, 120, 96], source = master_reservoir['A1'], dest = [reagent_plate_1['A1'], reagent_plate_1['A2'], reagent_plate_1['A3'], reagent_plate_1['A4']], blow_out = True)
    p1000.distribute(volume = [5,5,5,5], source = master_reservoir['A1'], dest = [ reagent_plate_1['A7'].bottom(z=0.5), reagent_plate_1['A8'].bottom(z=0.5), reagent_plate_1['A9'].bottom(z=0.5), reagent_plate_1['A10'].bottom(z=0.5)], blow_out = True, touch_tip = True)