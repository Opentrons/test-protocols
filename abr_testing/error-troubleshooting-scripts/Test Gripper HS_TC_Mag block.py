from opentrons import protocol_api

metadata = {
    'protocolName': 'Testing Gripper moves from Modules',
    'author': 'Rhyann Clarke: rhyann.clarke@opentrons.com',
    'description': 'Use parameters to select which module to heat up.'
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.20",
}

def run(protocol: protocol_api.ProtocolContext):
    thermocycler = protocol.load_module('thermocycler module gen2')
    heatershaker = protocol.load_module("heaterShakerModuleV1", "D1")
    hs_adapter          = heatershaker.load_adapter('opentrons_96_pcr_adapter')
    sample_plate     = hs_adapter.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    mag_block = protocol.load_module("magneticBlockV1", "C1")
    
    for i in range(50):
        heatershaker.open_labware_latch()
        thermocycler.open_lid()
        protocol.move_labware(sample_plate, mag_block, use_gripper = True)
        protocol.move_labware(sample_plate, thermocycler, use_gripper = True)
        thermocycler.close_lid()
        thermocycler.open_lid()
        protocol.move_labware(sample_plate, hs_adapter, use_gripper = True)
        heatershaker.close_labware_latch()
        protocol.comment(f"Move Cycle: {i}")
        