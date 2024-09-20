from opentrons import protocol_api
from opentrons.protocol_api import PARTIAL_COLUMN, SINGLE

metadata = {
    'protocolName': 'Testing Single Tip Pickup by Row with Nozzle A1 and H1',
    'author': 'Tony Ngumah: tony.ngumah@opentrons.com',
    'description': 'Test pyramis style pickup with 8ch'
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
    flex_pipette = protocol.params.flex_pipette
    # Set up labware
    tip_rack_1 = protocol.load_labware(tip_type, "D1")
    tip_rack_2 = protocol.load_labware(tip_type, "D2")
    tip_rack_3 = protocol.load_labware(tip_type, "D3")

    tip_rack_4 = protocol.load_labware(tip_type, "B1")
    tip_rack_5 = protocol.load_labware(tip_type, "B2")
    tip_rack_6 = protocol.load_labware(tip_type, "B3")


    trash_bin = protocol.load_trash_bin("A3")

    

    pipette = None
    if flex_pipette == "flex_8channel_1000":
        pipette = protocol.load_instrument(flex_pipette,  mount = "left")
    else:
        pipette = protocol.load_instrument(flex_pipette,  mount = "right")

    
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    def Reverse(lst):
        new_lst = lst[::-1]
        return new_lst
    rows_reversed = Reverse(rows)
    tip_rack_row_1 = [tip_rack_1, tip_rack_2, tip_rack_3]
    tip_rack_row_2 = [tip_rack_4, tip_rack_5, tip_rack_6]


    def row_pickup(tip_rack_row, rows):
        for rack in tip_rack_row:
            for row in rows:
                for col in range(1, 13):
                    tip_name = f"{row}{col}"
                    pipette.pick_up_tip(rack[tip_name])
                    pipette.drop_tip(trash_bin)

    pipette.configure_nozzle_layout(style = SINGLE, start="H1")
    row_pickup(tip_rack_row_1, rows)
    pipette.configure_nozzle_layout(style = SINGLE, start="A1")
    row_pickup(tip_rack_row_2, rows_reversed)
