from typing import List

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware, Well

metadata = {
    "protocolName": "8 channel Heater-Shaker testing",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "apiLevel": "2.13",
}

SCENARIO = "D"


class Scenario:
    def __init__(self, hs_position: str, tip_rack_position: str) -> None:
        self.hs_position: str = hs_position
        self.tip_rack_position: str = tip_rack_position


# WILL NOT WORK on ROBOT SIDE due to python 3.10 syntax used.


def get_scenario(scenario) -> str:
    """Get the positions for each scenario."""
    # http://sandbox.docs.opentrons.com/release_6.1.0/v2/new_modules.html#using-a-heater-shaker-module
    match scenario:
        case "A":
            # error
            # Cannot move pipette to Heater-Shaker or adjacent slot while module is shaking
            # tip rack back
            return Scenario(hs_position="1", tip_rack_position="4")
        case "B":
            # error
            # Cannot move pipette to Heater-Shaker or adjacent slot while module is shaking
            # tip rack front
            return Scenario(hs_position="4", tip_rack_position="1")
        case "C":
            # error
            # Cannot move pipette to Heater-Shaker or adjacent slot while module is shaking
            # tip rack right
            return Scenario(hs_position="1", tip_rack_position="2")
        case "D":
            # error
            # Cannot move pipette to Heater-Shaker or adjacent slot while module is shaking
            # tip rack left
            return Scenario(hs_position="3", tip_rack_position="2")


def run(context: protocol_api.ProtocolContext):

    scenario: Scenario = get_scenario(SCENARIO)

    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", scenario.hs_position)
    # Load adapter + labware on module.
    hs_plate = hs_mod.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")

    # 300ul tips
    tips_300ul: List[Labware] = [
        context.load_labware(
            load_name="opentrons_96_tiprack_300ul",
            location=scenario.tip_rack_position,
            label="300ul tips",
        )
    ]

    pipette_left: InstrumentContext = context.load_instrument(
        instrument_name="p300_multi_gen2", mount="left", tip_racks=tips_300ul
    )

    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(
        rpm=366
    )  # Waits until H/S has reached 366rpm speed
    pipette_left.pick_up_tip()
