from opentrons import protocol_api
from opentrons.protocol_api import SINGLE

metadata = {
    'protocolName': 'Testing Single Tip Pick Up',
    'author': 'Rhyann Clarke: rhyann.clarke@opentrons.com',
    'description': 'Use parameters to select which module to heat up.'
}

requirements = {
    "robotType": "OT-3",
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
    default = "opentrons_flex_96_tiprack_1000ul"
    )
    

def run(protocol: protocol_api.ProtocolContext):
    tip_type = protocol.params.tip_size
    
    trash_bin = protocol.load_trash_bin("B3")
    waste_chute = protocol.load_waste_chute()
    # Define Tip Racks
    if tip_type != "all":
        tip_rack_1 = protocol.load_labware(tip_type, "C3")
        tip_rack_2 = protocol.load_labware(tip_type, "C4")
        tip_rack_3 = protocol.load_labware(tip_type, "D4")
    else:
        tip_rack_1 = protocol.load_labware("opentrons_flex_96_tiprack_50ul", "C3")
        tip_rack_2 = protocol.load_labware("opentrons_flex_96_tiprack_200ul", "C4")
        tip_rack_3 = protocol.load_labware("opentrons_flex_96_tiprack_1000ul", "D4")
    
    tip_racks = [tip_rack_1, tip_rack_2, tip_rack_3]
    # Define Pipette
    pipette_96_channel = protocol.load_instrument("flex_96channel_1000", mount="left", tip_racks=tip_racks)

    # Define Labware
    source_reservoir = protocol.load_labware("nest_96_wellplate_2ml_deep", "D2")
    dest_pcr_plate = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "C2")
    # Load modules on deck
    thermocycler = protocol.load_module("thermocycler module gen2")
    # Single Tip Pick up
    def test_single_tip_pick_up(tip_rack):
        pipette_96_channel.configure_nozzle_layout(style=SINGLE, start="H12")
        tip_count = 0  # Tip counter to ensure proper tip usage
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']  # 8 rows
        columns = range(1, 13)  # 12 columns
        for row in rows:
            for col in columns:
                well_position = f"{row}{col}"
                pipette_96_channel.pick_up_tip(tip_rack) 

                pipette_96_channel.aspirate(5, source_reservoir[well_position])
                pipette_96_channel.touch_tip()

                pipette_96_channel.dispense(5, dest_pcr_plate[well_position].bottom(0.3))
                pipette_96_channel.drop_tip(trash_bin)
                tip_count+=1
        # leave this dropping in waste chute, do not use get_disposal_preference
        # want to test partial drop
        protocol.move_labware(tip_rack, waste_chute, use_gripper = True)
    
    # Iterate through all three tip racks
    test_single_tip_pick_up(tip_rack_1)
    protocol.move_labware(tip_rack_2, "C3", use_gripper = True)
    test_single_tip_pick_up(tip_rack_2)
    protocol.move_labware(tip_rack_3, "C3", use_gripper = True)
    test_single_tip_pick_up(tip_rack_3)