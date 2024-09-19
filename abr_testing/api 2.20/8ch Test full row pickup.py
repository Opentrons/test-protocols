from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, SINGLE

metadata = {
    'protocolName': 'Single and Partial Tip Pickup by Row for 8ch Pipette',
    'author': 'Tony Ngumah: tony.ngumah@opentrons.com',
    'description': 'Test partial pickup with 8ch by row'
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.20",
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
        {"display_name": "all", "value": "all"}
    ],
    default = "opentrons_flex_96_tiprack_50ul"
    )
    parameters.add_float(
        variable_name = "dot_bottom",
        display_name = ".bottom",
        description = "Lowest value pipette will go to.",
        default = 0.1,
        choices=[
            {"display_name": "0.0", "value": 0.0},
            {"display_name": "0.1", "value": 0.1},
            {"display_name": "0.2", "value": 0.2},
            {"display_name": "0.3", "value": 0.3},
            {"display_name": "0.4", "value": 0.4},
            {"display_name": "0.5", "value": 0.5},
            {"display_name": "0.6", "value": 0.6},
            {"display_name": "0.7", "value": 0.7},
            {"display_name": "0.8", "value": 0.8},
            {"display_name": "0.9", "value": 0.9},
            {"display_name": "1.0", "value": 1.0},
        ]
    )

    parameters.add_str(
        variable_name= "flex_pipette",
        display_name = "Pipette",
        description = "Set Flex Pipette",
        default = "flex_8channel_1000",
        choices=[
            {"display_name": "Flex 8ch 1000ul", "value": "flex_8channel_1000"},
            {"display_name": "Flex 8ch 50ul", "value": "flex_8channel_50"},
        ]
    )
    
def run(protocol: protocol_api.ProtocolContext):
    tip_type = protocol.params.tip_size
    dot_bottom = protocol.params.dot_bottom
    flex_pipette = protocol.params.flex_pipette
    # Set up labware
    tip_rack_1 = protocol.load_labware(tip_type, "D1")
    tip_rack_2 = protocol.load_labware(tip_type, "D2")
    tip_rack_3 = protocol.load_labware(tip_type, "D3")
    tip_rack_4 = protocol.load_labware(tip_type, "B1")

    tip_rack_5 = protocol.load_labware(tip_type, "B2")
    tip_rack_6 = protocol.load_labware(tip_type, "B3")
    tip_rack_7 = protocol.load_labware(tip_type, "D4")

    trash_bin = protocol.load_trash_bin("A3")

    

    pipette = None
    if flex_pipette == "flex_8channel_1000":
        pipette = protocol.load_instrument("flex_8channel_1000",  mount = "left")
    else:
        pipette = protocol.load_instrument("flex_8channel_50",  mount = "right")

    
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]

    def adjust_start_end(num_tips):
        protocol.comment("Changing Nozzle Configuration")
        if num_tips == 2:
            pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end="G1")
        elif num_tips == 3:
            pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end="F1")
        elif num_tips == 1:
            pipette.configure_nozzle_layout(style=SINGLE, start="H1")

    def clear_rack(rack, num_tips):
        adjust_start_end(num_tips)
        row = rows[len(rows) - 1]
        protocol.comment("Row: " + str(row))
        for col in range(1,13):
            tip_name = f"{row}{col}"
            pipette.pick_up_tip(rack[tip_name])
            pipette.drop_tip(trash_bin)
    def row_pickup(rack, num_tips):
        idx = 1
        for row in rows:
            if idx % num_tips == 0:
                for col in range(1, 13):
                    tip_name = f"{row}{col}"
                    pipette.pick_up_tip(rack[tip_name])
                    pipette.drop_tip(trash_bin)
            idx += 1
        if 8 % num_tips != 0:
            clear_rack(rack, 8%num_tips)

    # Single tip pickup with rack 1
    pipette.configure_nozzle_layout(style=SINGLE, start="H1")
    row_pickup(tip_rack_1, 1)

    # 2 tip pickup with rack 2
    pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end = "G1")
    row_pickup(tip_rack_2, 2)

    # 3 tip pickup with rack 3
    pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end = "F1")
    row_pickup(tip_rack_3, 3)

    # 4 tip pickup with rack 4
    pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end = "E1")
    row_pickup(tip_rack_4, 4)

    # 5 tip pickup with rack 5
    pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end = "D1")
    row_pickup(tip_rack_5, 5)

    # 6 tip pickup with rack 6
    pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end = "C1")
    row_pickup(tip_rack_6, 6)


    # Move tip rack 7 into deck slot B3
    protocol.move_labware(
        labware=tip_rack_6,
        new_location="A1",
        use_gripper=True
    )

    protocol.move_labware(
        labware=tip_rack_7,
        new_location="B3",
        use_gripper=True
    )
    # 7 tip pickup with rack 7
    pipette.configure_nozzle_layout(style=PARTIAL_COLUMN, start="H1", end = "B1")
    row_pickup(tip_rack_7, 7)
