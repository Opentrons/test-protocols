# Liquid Set up

from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Trash Chute Liquid Run Set Up',
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
    tiprack_1000b       = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='C1') # Tip Rack
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    deep1               = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'D2')
    deep2               = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'D3')
    deep3               = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'C2')
    deep4               = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'B2')
    deep5               = protocol.load_labware('nest_96_wellplate_2ml_deep', location = 'B3')
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000a, tiprack_1000b]) # Pipette
    
    columns =['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
    for i in columns:
        p1000.pick_up_tip()
        #p1000.well_bottom_clearance.aspirate = 1
        p1000.aspirate(1000, master_reservoir['A1'].bottom(z=0.5))
        p1000.dispense(1000, deep1[i].bottom(z=1))
        p1000.return_tip()
    for i in columns:
        p1000.pick_up_tip()
        #p1000.well_bottom_clearance.aspirate = 1
        p1000.aspirate(1000, master_reservoir['A1'].bottom(z=0.5))
        p1000.dispense(1000, deep2[i].bottom(z=1))
        p1000.return_tip()
    for i in columns:
        p1000.pick_up_tip()
        #p1000.well_bottom_clearance.aspirate = 1
        p1000.aspirate(1000, master_reservoir['A1'].bottom(z=0.5))
        p1000.dispense(1000, deep3[i].bottom(z=1))
        p1000.return_tip()
    for i in columns:
        p1000.pick_up_tip()
        #p1000.well_bottom_clearance.aspirate = 1
        p1000.aspirate(500, master_reservoir['A1'].bottom(z=0.5))
        p1000.dispense(500, deep4[i].bottom(z=1))
        p1000.return_tip()
    for i in columns:
        p1000.pick_up_tip()
        #p1000.well_bottom_clearance.aspirate = 1
        p1000.aspirate(500, master_reservoir['A1'].bottom(z=0.5))
        p1000.dispense(500, deep5[i].bottom(z=1))
        p1000.return_tip()

