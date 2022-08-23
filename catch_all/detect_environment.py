"""Smoke Test 6.0"""
import os

from opentrons import protocol_api

metadata = {
    # "protocolName": f"🛠 Test {os.path.basename(__file__)} 🛠",
    "protocolName": "🛠 Test Detect Environment 🛠",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": "Description value",
    "apiLevel": "2.12",
}

# ssh into robot and then did
# printenv
# picked a variable


def on_robot() -> bool:
    smoothie: str = os.getenv("OT_SMOOTHIE_ID", "")
    if smoothie != "":
        return True
    return False


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    if ctx.is_simulating() and not on_robot():
        # test with
        # PATH/python3 -m opentrons.cli analyze --json-output=/PATH/x.json PATH/detect_environment.py
        ctx.comment("I am simulating not on the robot")
    elif ctx.is_simulating() and on_robot():
        ctx.comment("I am simulating on the robot")
    elif not ctx.is_simulating():
        ctx.comment("Protocol is running.")
    else:
        ctx.comment("I am running in a dimension not perceived.")
