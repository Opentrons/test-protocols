from opentrons import protocol_api

metadata = {
    "protocolName": "not python syntax",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("iamnotPython()"),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""
    ctx.comment("Hello world")
    iamnotPython()
