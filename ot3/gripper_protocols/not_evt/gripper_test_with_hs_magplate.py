from typing import Mapping
from opentrons.protocol_api import ProtocolContext
from opentrons.types import Mount, Point

######### Initial Deck Setup #########
# Slot 1: Tiprack- opentrons_ot3_96_tiprack_50ul
# Slot 2: Mag plate
# Slot 3: Heater-Shaker
# Slot 4: Armadillo 96 wellplate moved here
# Slot 5: First Armadillo 96 wellplate loaded here
# Slot 6: Second Armadillo 96 wellplate loaded here.
# 
######################################

metadata = {
    "name": "Gripper collision avoidance test protocol",
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.13",
}

MAG_PLATE_SLOT=2

hs_labware_offset_z = 68.275


pick_up_deck_slot_offset_dict = {"x": -0.25, "y": 0, "z": 0}

def point_to_dict(offset: Point) -> Mapping[str, float]:
    return {"x": offset.x, "y": offset.y, "z": offset.z}

mag_plate_offset = Point(x=0, y=0, z=29.5)
pick_up_mag_plate_offset = mag_plate_offset + Point(x=0, y=0, z=0)
drop_off_mag_plate_offset = mag_plate_offset + Point(x=0, y=0, z=2)

hs_z_offset = Point(x=-3, y=-1, z=24 - 68.275)
pick_up_hs_z_offset = hs_z_offset + Point(x=0, y=0, z=0)
drop_off_hs_z_offset = hs_z_offset + Point(x=0, y=0, z=-2)


def run(protocol: ProtocolContext) -> None:
    """Simple gripper test protocol."""
    tip_rack = protocol.load_labware(
        "opentrons_ot3_96_tiprack_50ul",
        location="1",
    )
    well_plate_1 = protocol.load_labware(
        "armadillo_96_wellplate_200ul_pcr_full_skirt",
        location="5",
    )
    pipette = protocol.load_instrument("p1000_single_gen3", mount=Mount.LEFT, tip_racks=[tip_rack])
    heater_shaker = protocol.load_module("heaterShakerModuleV1", 3)
    # well_plate_2 = protocol.load_labware(
    #     "armadillo_96_wellplate_200ul_pcr_full_skirt",
    #     location="6",
    # )

    heater_shaker.close_labware_latch()
    pipette.pick_up_tip()
    pipette.aspirate(10, well_plate_1['A1'])
    pipette.dispense(10, well_plate_1['A1'])

    #### Move armadillo plate from slot 5 to Mag plate ####
    protocol.move_labware(
        labware=well_plate_1,
        new_location=MAG_PLATE_SLOT,
        use_gripper=True,
        use_pick_up_location_lpc_offset=False,
        use_drop_location_lpc_offset=False,
        pick_up_offset=pick_up_deck_slot_offset_dict,
        drop_offset=point_to_dict(drop_off_mag_plate_offset),
    )

    pipette.aspirate(10, well_plate_1['A1'])
    pipette.dispense(10, well_plate_1['A1'])
    heater_shaker.open_labware_latch()
    
    #### Move armadillo plate from Mag plate to heater-shaker ####
    protocol.move_labware(
        labware=well_plate_1,
        new_location=heater_shaker,
        use_gripper=True,
        use_pick_up_location_lpc_offset=False,
        use_drop_location_lpc_offset=False,
        pick_up_offset=point_to_dict(pick_up_mag_plate_offset),
        drop_offset=point_to_dict(drop_off_hs_z_offset),
    )
    heater_shaker.close_labware_latch()
    pipette.aspirate(10, well_plate_1['A1'])
    pipette.dispense(10, well_plate_1['A1'])

    pipette.aspirate(10, well_plate_1['A1'])
    pipette.blow_out()
    heater_shaker.open_labware_latch()
    
    #### Move armadillo plate from heater-shaker to Slot 4 ####
    protocol.move_labware(
        labware=well_plate_1,
        new_location="4",       # Empty slot
        use_gripper=True,
        use_pick_up_location_lpc_offset=False,
        use_drop_location_lpc_offset=False,
        pick_up_offset=point_to_dict(pick_up_hs_z_offset),
        drop_offset={"x": 0, "y": 0, "z": 0},
    )
    pipette.drop_tip()
