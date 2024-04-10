from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Temperature Module Ramp Rate',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.17",
}

def run(protocol: protocol_api.ProtocolContext):
    temp_deck = protocol.load_module('temperature module gen2', 'D3')
    current_temp = temp_deck.temperature
    protocol.comment(f"Temperature Module Temp: {str(current_temp)}")
    temp_deck.set_temperature(22)
    protocol.delay(minutes=5)
    temp_deck.set_temperature(4)
    protocol.delay(minutes=5)
    temp_deck.set_temperature(95)
    protocol.delay(minutes=5)
    temp_deck.deactivate()