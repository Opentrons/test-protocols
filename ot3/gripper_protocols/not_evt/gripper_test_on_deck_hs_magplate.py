from typing import Mapping
from opentrons.protocol_api import ProtocolContext
from opentrons.types import Mount

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


def grip_offset(action, item):
    from opentrons.types import Point
    # do NOT edit these values
    # NOTE: these values will eventually be in our software
    #       and will not need to be inside a protocol
    _hw_offsets = {
        "deck": Point(),
        "mag-plate": Point(z=29.5),
        "heater-shaker": Point(x=-3, y=-1, z=(24 - 68.275)),
        "temp-module": Point(),
        "thermo-cycler": Point()
    }
    # EDIT these values
    # NOTE: we are still testing to determine our software's defaults
    #       but we also expect users will want to edit these
    _pick_up_offsets = {
        "deck": Point(x=-0.2),
        "mag-plate": Point(),
        "heater-shaker": Point(),
        "temp-module": Point(),
        "thermo-cycler": Point()
    }
    # EDIT these values
    # NOTE: we are still testing to determine our software's defaults
    #       but we also expect users will want to edit these
    _drop_offsets = {
        "deck": Point(z=-2),
        "mag-plate": Point(z=9.5),
        "heater-shaker": Point(z=-2),
        "temp-module": Point(z=-2),
        "thermo-cycler": Point()
    }
    # make sure arguments are correct
    action_options = ["pick-up", "drop"]
    item_options = list(_hw_offsets.keys())
    if action not in action_options:
        raise ValueError(f"\"{action}\" not recognized, available options: {action_options}")
    if item not in item_options:
        raise ValueError(f"\"{item}\" not recognized, available options: {item_options}")
    # add up the combined offset
    hw_offset = _hw_offsets[item]
    if action == "pick-up":
        offset = hw_offset + _pick_up_offsets[item]
    elif action == "drop":
        offset = hw_offset + _drop_offsets[item]
    # convert from Point() to dict()
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
            pick_up_offset=grip_offset("pick-up", "heater-shaker"),
            drop_offset=grip_offset("drop", "mag-plate"),
        )
        #### Move armadillo plate from Mag plate to h/s ####
        protocol.move_labware(
            labware=well_plate_1,
            new_location=heater_shaker,
            use_gripper=True,
            pick_up_offset=grip_offset("pick-up", "mag-plate"),
            drop_offset=grip_offset("drop", "heater-shaker"),
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
