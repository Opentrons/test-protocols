"""Smoke Test 6.0"""
import os
from typing import List, Optional

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware, Well

metadata = {
    "protocolName": f"🛠 Test ?????? 🛠",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": "Description Value",
    "apiLevel": "2.12",
}


def run(protocol_context: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    # deck positions
    tips_300ul_position = "1"
    dye_source_postion = "2"
    logo_position = "3"
    temperature_position = "4"
    tips_20ul_position = "5"
    custom_lw_position = "6"
    magnetic_position = "9"
    # Thermocycler has a default position that covers Slots 7, 8, 10, and 11.
    # This is the only valid location for the Thermocycler on the OT-2 deck.

    # 300ul tips
    tips_300ul: List[Labware] = [
        protocol_context.load_labware(
            load_name="opentrons_96_tiprack_300ul", location=tips_300ul_position, label="300ul tips"
        )
    ]

    # 20ul tips
    tips_20ul: List[Labware] = [
        protocol_context.load_labware(
            load_name="opentrons_96_tiprack_20ul", location=tips_20ul_position, label="20ul tips"
        )
    ]

    # pipettes
    pipette_right: InstrumentContext = protocol_context.load_instrument(
        instrument_name="p20_single_gen2", mount="right", tip_racks=tips_20ul
    )

    pipette_left: InstrumentContext = protocol_context.load_instrument(
        instrument_name="p300_multi_gen2", mount="left", tip_racks=tips_300ul
    )


    # modules
    magnetic_module = protocol_context.load_module("magnetic module gen2", magnetic_position)
    temperature_module = protocol_context.load_module("temperature module", temperature_position)
    thermocycler_module = protocol_context.load_module("thermocycler module")

 