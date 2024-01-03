from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Kapa Library Quant v4.8 Liquid Set Up',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

# Protocol to fill sample plate, reagent plate, and reservoir for Kapa Library Quant v4.8
# Weigh plates before and after run

def run(protocol: protocol_api.ProtocolContext):
    # Initiate Labware
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    reservoir           = protocol.load_labware('nest_12_reservoir_15ml','D2') # Reservoir
    sample_plate_1      = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt",'D3') # Sample Plate
    reagent_plate_1     = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt",'C3') # Reagent Plate
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000]) # Pipette

    # Sample Plate Prep: dispense 30 ul into columns 1 - 6 - total 1440 ul
    p1000.distribute(volume = [30, 30, 30, 30, 30, 30], source = master_reservoir['A1'].bottom(z=0.5), dest = [sample_plate_1['A1'], sample_plate_1['A2'], sample_plate_1['A3'], sample_plate_1['A4'], sample_plate_1['A5'], sample_plate_1['A6']], blow_out = True, blow_out_location = 'source well', trash = False)

    # Reservoir Plate Prep: 14 mL into column 5
    p1000.transfer(volume = 1750, source = master_reservoir['A1'].bottom(z=0.5), dest = reservoir['A5'].top(), blow_out = True, blow_out_location = 'source well', trash = False)

    # Reagent Plate Prep: dispense 30 and 200 ul into columns 1 and 3 - total 1840 ul
    p1000.distribute(volume = [30, 200], source = master_reservoir['A1'].bottom(z=0.5), dest = [reagent_plate_1['A1'], reagent_plate_1['A3']], blow_out = True, blow_out_location = 'source well', trash = False)
    
    
