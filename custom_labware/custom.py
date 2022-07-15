"""Smoke Test 6.0"""
from typing import List, Optional

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware, Well

metadata = {
    "protocolName": "Custom Labware and some steps",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("Custom Labware and some delays."),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    custom_labware = ctx.load_labware(
        "cpx_4_tuberack_100ul",
        "8",
        "4 tubes",
        "custom_beta",
    )
    ctx.delay(seconds=4)
    ctx.delay(seconds=4)
    for i in range(0, 5):
        ctx.comment(f"A range of comments n={str(i)}")
    ctx.pause("You must scroll to see me!")
