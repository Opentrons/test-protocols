from opentrons import protocol_api

metadata = {
    'protocolName': 'Throw out Liquid Filled Tips (1000, 200, 50)',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
}
requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.16'
}

def run(protocol: protocol_api.ProtocolContext):
    # Waste Chute
    waste_chute = protocol.load_waste_chute()
    
    # Initiate Labware
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='A2', adapter = "opentrons_flex_96_tiprack_adapter") 
    tiprack_200         = protocol.load_labware(load_name='opentrons_flex_96_tiprack_200ul', location='B2', adapter = "opentrons_flex_96_tiprack_adapter")
    tiprack_50         = protocol.load_labware(load_name='opentrons_flex_96_tiprack_50ul', location='C2', adapter = "opentrons_flex_96_tiprack_adapter")
    master_reservoir    = protocol.load_labware(load_name = 'axygen_1_reservoir_90ml', location='D2')
    # Pipette
    p96               = protocol.load_instrument(instrument_name='flex_96channel_1000', mount='left', tip_racks=[tiprack_1000, tiprack_200, tiprack_50]) 
    
    # Protocol Steps
    p96.pick_up_tip(tiprack_50)
    p96.aspirate(50, master_reservoir['A1'].bottom(z=1))
    p96.drop_tip()
    
    p96.pick_up_tip(tiprack_200)
    p96.aspirate(200, master_reservoir['A1'].bottom(z=1))
    p96.drop_tip()
    
    p96.pick_up_tip(tiprack_1000)
    p96.aspirate(1000, master_reservoir['A1'].bottom(z=1))
    p96.drop_tip()