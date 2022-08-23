from opentrons import protocol_api

metadata = {
    "protocolName": "Will fail on run",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("A single comment"),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""
    ctx.comment("one comment")
    if not ctx.is_simulating():
        raise RuntimeError("oh shit")
