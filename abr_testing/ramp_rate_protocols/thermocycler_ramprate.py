from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Thermocycler Ramp Rate',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.17",
}

def run(protocol: protocol_api.ProtocolContext):
    thermocycler        = protocol.load_module('thermocycler module gen2', "B1")
    
    # Set lid to 105 C
    thermocycler.close_lid()
    block_temp = thermocycler.block_temperature
    protocol.comment(f"Thermocycler block temp: {str(block_temp)}")
    thermocycler.set_lid_temperature(105)
    thermocycler.set_block_temperature(4, hold_time_minutes = 5)
    thermocycler.set_block_temperature(99, hold_time_minutes = 5)
    thermocycler.set_block_temperature(4, hold_time_minutes = 5)
    thermocycler.deactivate_lid()
    thermocycler.deactivate_block()
    