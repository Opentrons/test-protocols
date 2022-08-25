
metadata = {
    "protocolName": "DeckConflictError Tall Heater-Shaker testing",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "apiLevel": "2.13",
}

SCENARIO = "A"


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
            # No error - can be adjacent
            return Scenario(hs_position="1", module_position="4")
        case "B":
            # Error - Cannot be right
            return Scenario(hs_position="1", module_position="2")
        case "C":
            # Error - Cannot be left
            return Scenario(hs_position="3", module_position="2")


def run(context):

    scenario: Scenario = get_scenario(SCENARIO)

    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", scenario.hs_position)
    # Load adapter + labware on module.
    hs_plate = hs_mod.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")

    # Load Tall Labware
    labware = context.load_labware(
        "opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical", scenario.module_position
    )
