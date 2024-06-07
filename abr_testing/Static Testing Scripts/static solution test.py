from opentrons import protocol_api
from opentrons import types


metadata = {
    'protocolName': 'static solution test',
    'author': 'Nick Shiland <nicholas.shiland@opentrons.com>',
    'source': 'Protocol Library'
    }


requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.18",
}

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="repetitions",
        display_name="Cycle Repetitions",
        description="Set Number of Times to Repeat Cycle",
        default = 5,
        minimum = 1,
        maximum = 150,
        unit = "times",
    )

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE    
    tiprack_1        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'D1')
    pcr_plate        = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', location = 'B3')
    reservoir        = protocol.load_labware('nest_12_reservoir_15ml', location = 'D3')
    repetitions = protocol.params.repetitions
    # Pipette
    pleft = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_1])
    #tip rack columns
    tiprack_columns = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]



    for i in list(range(repetitions)):
        for column in tiprack_columns:
            pleft.pick_up_tip(tiprack_1[column])
            pleft.aspirate(50, reservoir[column])
            pleft.dispense(10, pcr_plate[column])
            pleft.return_tip()
            protocol.move_labware(tiprack_1, "A1", use_gripper = False)
            pleft.move_to(tiprack_1[column].top())
            pleft.dispense(40)
        pleft.reset_tipracks()