from typing import Mapping
from opentrons.protocol_api import ProtocolContext
from opentrons.types import Mount, Point

######### Initial Deck Setup #########
# Slot 1: Tiprack- opentrons_ot3_96_tiprack_50ul
# Slot 3: Heater-Shaker
# 
######################################

metadata = {
    "name": "Gripper w/ H/S test protocol"
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.13",
}



# do NOT edit any of the below values
pick_up_deck_slot_offset = Point(x=-0.2) # do NOT edit
mag_plate_offset = Point(z=29.5)  # do NOT edit
hs_labware_offset_z_on_ot2 = 68.275  # do NOT edit
hw_labware_offset_z_on_ot3 = 24  # do NOT edit
hw_labware_offset_z_workaround = hw_labware_offset_z_on_ot3 - hs_labware_offset_z_on_ot2
hs_z_offset = Point(x=-3, y=-1, z=hw_labware_offset_z_workaround)  # do NOT edit

# EDIT these values below
# pick-up and drop offsets
pick_up_mag_plate_offset = mag_plate_offset + Point(z=0)
drop_off_mag_plate_offset = mag_plate_offset + Point(z=9.5)
pick_up_hs_z_offset = hs_z_offset + Point()
drop_off_hs_z_offset = hs_z_offset + Point(z=-2)



def point_to_dict(offset: Point) -> Mapping[str, float]:
    return {"x": offset.x, "y": offset.y, "z": offset.z}


def run(protocol: ProtocolContext) -> None:
    """Simple gripper test protocol."""
    tip_rack = protocol.load_labware(
        "opentrons_ot3_96_tiprack_50ul",
        location="1",
    )

    pipette = protocol.load_instrument("p1000_single_gen3", mount=Mount.LEFT, tip_racks=[tip_rack])
    heater_shaker = protocol.load_module("heaterShakerModuleV1", 3)
    well_plate_1 = heater_shaker.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")

    heater_shaker.close_labware_latch()

    def do_gripper_stuff():
        heater_shaker.open_labware_latch()
        #### Move armadillo plate from h/s to Mag plate ####
        protocol.move_labware(
            labware=well_plate_1,
            new_location=2,
            use_gripper=True,
            use_pick_up_location_lpc_offset=False,
            use_drop_location_lpc_offset=False,
            pick_up_offset=point_to_dict(pick_up_hs_z_offset),
            drop_offset=point_to_dict(drop_off_mag_plate_offset),
        )
        #### Move armadillo plate from Mag plate to h/s ####
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

    do_gripper_stuff()

    heater_shaker.close_labware_latch()
    pipette.pick_up_tip()
    pipette.aspirate(10, well_plate_1['A1'])
    pipette.dispense(10, well_plate_1['A1'])
    pipette.drop_tip()

    do_gripper_stuff()
    protocol.home()

    do_gripper_stuff()
