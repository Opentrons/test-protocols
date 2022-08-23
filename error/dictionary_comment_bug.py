from opentrons import protocol_api

metadata = {
    "protocolName": "🛠 Test Dictionary as comment🛠",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("comment in commands response is not a string"),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""
    a_dictionary = {"key": "value"}
    ctx.comment(a_dictionary)
    ctx.comment("I am string.")
