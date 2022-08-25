import time
from ast import mod

metadata = {
    "protocolName": "DeckConflictError Heater-Shaker testing",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "apiLevel": "2.13",
}

SCENARIO = "T"


class Scenario:
    def __init__(self, hs_position: str, module_position: str) -> None:
        self.hs_position: str = hs_position
        self.module_position: str = module_position


# WILL NOT WORK on ROBOT SIDE due to python 3.10 syntax used.


def get_scenario(scenario) -> str:
    """Get the positions for each scenario."""
    # http://sandbox.docs.opentrons.com/release_6.1.0/v2/new_modules.html#using-a-heater-shaker-module
    match scenario:
        case "A":
            # No error
            return Scenario(hs_position="1", module_position="3")
        case "B":
            # Error - Adjacent
            return Scenario(hs_position="1", module_position="2")
        case "C":
            # Error - Adjacent
            return Scenario(hs_position="1", module_position="4")
        case "D":
            # Error - Adjacent
            return Scenario(hs_position="4", module_position="1")
        case "E":
            # Error - Adjacent
            return Scenario(hs_position="4", module_position="5")
        case "F":
            # Error - Adjacent
            return Scenario(hs_position="4", module_position="7")
        case "G":
            # Error - Adjacent
            return Scenario(hs_position="7", module_position="4")
        case "H":
            # Error - Adjacent
            return Scenario(hs_position="7", module_position="8")
        case "I":
            # Error - Adjacent
            return Scenario(hs_position="7", module_position="10")
        case "J":
            # Error - Adjacent
            return Scenario(hs_position="10", module_position="11")
        case "K":
            # Error - Adjacent
            return Scenario(hs_position="10", module_position="7")
        case "L":
            # Error - Adjacent
            return Scenario(hs_position="3", module_position="2")
        case "M":
            # Error - Adjacent
            return Scenario(hs_position="3", module_position="6")
        case "N":
            # Error - Adjacent
            return Scenario(hs_position="6", module_position="3")
        case "O":
            # Error - Adjacent
            return Scenario(hs_position="6", module_position="5")
        case "P":
            # Error - Adjacent
            return Scenario(hs_position="6", module_position="9")
        case "Q":
            # Error - Not allowed in 9 due to trash
            return Scenario(hs_position="9", module_position="1")
        case "R":
            # Error - Not allowed in 11 due to trash
            return Scenario(hs_position="11", module_position="1")
        case "S":
            # No Error - slot 2 is allowed but not recommended.
            return Scenario(hs_position="2", module_position="4")
        case "T":
            # Error - Adjacent - slot 2 is allowed but not recommended.
            return Scenario(hs_position="2", module_position="5")


def run(context):

    scenario: Scenario = get_scenario(SCENARIO)

    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", scenario.hs_position)
    # Load adapter + labware on module.
    hs_plate = hs_mod.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")

    # Load Mag module
    magnetic_module = context.load_module(
        "magnetic module gen2", scenario.module_position
    )
