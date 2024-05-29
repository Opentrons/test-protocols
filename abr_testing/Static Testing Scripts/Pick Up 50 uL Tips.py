from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Pick Up Tips Right and Left - 5 racks',
    'author': 'Nick Shiland <nicholas.shiland@opentrons.com>',
    'source': 'Protocol Library'
    }

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.18",
}

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_str(
        variable_name="tip_size",
        display_name="Tip Size",
        description="Set Left Pipette Tip Size",
        choices=[
        {"display_name": "50 uL", "value": "opentrons_flex_96_tiprack_50ul"},
        {"display_name": "200 µL", "value": "opentrons_flex_96_tiprack_200ul"},
        {"display_name": "1000 µL", "value": "opentrons_flex_96_tiprack_1000ul"},
    ],
    default = "opentrons_flex_96_tiprack_50ul"
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
        variable_name="right_pipette",
        display_name="Pipette Type Right Mount",
        description="Set Right Pipette Type",
        choices=[
        {"display_name": "1-Channel 50 µL", "value": "flex_1channel_50"},
        {"display_name": "8-Channel 50 µL", "value": "flex_8channel_50"},
        {"display_name": "1-Channel 1000 µL", "value": "flex_1channel_1000"},
        {"display_name": "8-Channel 1000 µL", "value": "flex_8channel_1000"},
    ],
    default = "flex_8channel_1000"
    )
    parameters.add_bool(
        variable_name= "tip_selection",
        display_name="Use Entire Tip Rack?",
        description="Do you want to use the entire tip rack?",
    default = True
    )

def run(protocol: protocol_api.ProtocolContext):
    left_pipette = protocol.params.left_pipette
    right_pipette = protocol.params.right_pipette
    tip_size = protocol.params.tip_size
    tip_selection = protocol.params.tip_selection
    # DECK SETUP AND LABWARE     
    tiprack_1        = protocol.load_labware(tip_size, location = 'A2')
    tiprack_2        = protocol.load_labware(tip_size, location = 'B2')
    tiprack_3        = protocol.load_labware(tip_size, location = 'C2')
    tiprack_4        = protocol.load_labware(tip_size, location = 'B3')
    tiprack_5        = protocol.load_labware(tip_size, location = 'C3')

    # Pipette
    pleft = protocol.load_instrument(left_pipette, "left", tip_racks=[tiprack_1,tiprack_2, tiprack_3, tiprack_4, tiprack_5])
    pright = protocol.load_instrument(right_pipette, "right", tip_racks=[tiprack_1,tiprack_2, tiprack_3, tiprack_4, tiprack_5])
    
    if tip_selection == True:
        for i in list(range(4)):
            for i in list(range(60)):
                pleft.pick_up_tip()
                pleft.return_tip()
            pleft.reset_tipracks()
            for i in list(range(60)):
                pright.pick_up_tip()
                pright.return_tip()
            pright.reset_tipracks()

    else:
        for i in list(range(60)):
            pleft.pick_up_tip()
            pleft.return_tip()
            pleft.reset_tipracks()
        