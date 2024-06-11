from opentrons import protocol_api
from opentrons import types


metadata = {
    'protocolName': 'static good view',
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
    parameters.add_str(
        variable_name="left_pipette",
        display_name="Pipette Type Left Mount",
        description="Set Left Pipette Type",
        choices=[
        {"display_name": "1-Channel 50 µL", "value": "flex_1channel_50"},
        {"display_name": "8-Channel 50 µL", "value": "flex_8channel_50"},
        {"display_name": "1-Channel 1000 µL", "value": "flex_1channel_1000"},
        {"display_name": "8-Channel 1000 µL", "value": "flex_8channel_1000"},
    ],
    default = "flex_8channel_1000"
    )
    parameters.add_str(
        variable_name="tiprack_size",
        display_name="Tiprack Used",
        description="Set Tiprack Type",
        choices=[
        {"display_name": "50 µL", "value": "opentrons_flex_96_tiprack_50ul"},
        {"display_name": "200 µL", "value": "opentrons_flex_96_tiprack_200ul"},
        {"display_name": "1000 µL", "value": "opentrons_flex_96_tiprack_1000ul"},
    ],
    default = "opentrons_flex_96_tiprack_50ul"
    )
    parameters.add_int(
        variable_name="wait_time",
        display_name="Wait Time",
        description="How long to wait after ejecting",
        default = 0,
        minimum = 2,
        maximum = 20,
        unit = "sec",
    )

def run(protocol: protocol_api.ProtocolContext):
    left_pipette = protocol.params.left_pipette
    tiprack_size = protocol.params.tiprack_size
    wait_time = protocol.params.wait_time
    # DECK SETUP AND LABWARE    
    tiprack_1        = protocol.load_labware(tiprack_size, location = 'D1')
    pcr_plate        = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', location = 'B3')
    reservoir        = protocol.load_labware('nest_12_reservoir_15ml', location = 'D3')
    repetitions = protocol.params.repetitions
    # Pipette
    pleft = protocol.load_instrument(left_pipette, "left", tip_racks=[tiprack_1])
    tiprack_columns = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]
   
    for i in list(range(repetitions)):
        for column in tiprack_columns:
            pleft.pick_up_tip(tiprack_1[column])
            pleft.aspirate(50, reservoir[column])
            pleft.dispense(10, pcr_plate[column])
            pleft.drop_tip(tiprack_1[column])
            protocol.delay(seconds=wait_time)
            pleft.home()
        pleft.reset_tipracks()

    #pcr_plate["A1"].top()
    #add mix
        
        #pleft.aspirate(40, pcr_plate["A1"])
        #pleft.move_to(reservoir["A1"].bottom())
        #pleft.dispense(40, pcr_plate["A1"])
    #touch tip with z offset using fur inside a 1well
