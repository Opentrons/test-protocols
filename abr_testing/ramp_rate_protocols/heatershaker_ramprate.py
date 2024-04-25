from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Heatershaker Ramp Rate',
    'author': 'Rhyann Clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.17",
}

def run(protocol: protocol_api.ProtocolContext):
    heatershaker        = protocol.load_module('heaterShakerModuleV1',"D1")
    
    heatershaker.set_and_wait_for_temperature(37)
    protocol.delay(minutes=5)
    heatershaker.set_and_wait_for_temperature(95)
    protocol.delay(minutes=5)
    heatershaker.set_and_wait_for_temperature(37)
    protocol.delay(minutes=5)
    heatershaker.deactivate_heater()
    