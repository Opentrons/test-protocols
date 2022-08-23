import pandas as pd
from opentrons import protocol_api

metadata = {
    "protocolName": "smol",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("A single comment"),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""
    dates = pd.Series([1, 3, 5, 6, 8])
    ctx.comment(str(dates))
