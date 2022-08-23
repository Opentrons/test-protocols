"""Smoke Test 6.0"""
import os
from dataclasses import dataclass
from pathlib import Path

from opentrons import protocol_api

metadata = {
    "protocolName": "🛠 File Read 🛠",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": "Example to Read a file across all analyses and run.",
    "apiLevel": "2.12",
}


# Felt a little cleaner than a dictionary?
@dataclass
class FilePathMapper:
    local: str
    robot: str


# Create some constants to store the filepaths for the files we need to read.
CSV_FILEPATH: FilePathMapper = FilePathMapper(
    local="/local/path/to/my_data.csv", robot="/robot/path/to/my_data.csv"
)
NAME_FILEPATH: FilePathMapper = FilePathMapper(
    local="/local/path/to/my_name.txt", robot="/robot/path/to/my_name.txt"
)


def on_robot() -> bool:
    """Am I on an OT robot?"""
    smoothie: str = os.getenv("OT_SMOOTHIE_ID", "")
    if smoothie != "":
        return True
    return False


def get_filepath(
    ctx: protocol_api.ProtocolContext, file_path_mapper: FilePathMapper
) -> Path:
    """Return the filepath based on the runtime environment."""
    if ctx.is_simulating() and not on_robot():
        ctx.comment("I am simulating and I am NOT on the robot.")
        return Path(file_path_mapper.local)
    elif ctx.is_simulating() and on_robot():
        ctx.comment("I am simulating on the robot")
        return Path(file_path_mapper.robot)
    elif not ctx.is_simulating():
        ctx.comment("Protocol is running.")
        return Path(file_path_mapper.robot)
    else:
        raise NotImplementedError("Unexpected runtime.")


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    csv_filepath = get_filepath(ctx=ctx, file_path_mapper=CSV_FILEPATH)
    ctx.comment(f"Filepath for my csv is {csv_filepath}")
    name_filepath = get_filepath(ctx=ctx, file_path_mapper=NAME_FILEPATH)
    ctx.comment(f"Filepath for my name file is {name_filepath}")
