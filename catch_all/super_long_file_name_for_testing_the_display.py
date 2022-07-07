"""Pause counter example."""
import time

from opentrons import protocol_api

metadata = {
    "protocolName": "super long protocol name for testing the display please and thank you",
    "author": "Opentrons <protocols@opentrons.com>",
    "source": "Example",
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""
    ctx.delay(20)
