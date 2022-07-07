"""Smoke Test 6.0"""
from typing import List, Optional

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware, Well

metadata = {
    "protocolName": "🛠MoaM🛠",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("🧲 🧲 Modules"),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    # deck positions
    dye_source_postion = "2"
    magnetic_position_2 = "9"
    tips_20ul_position = "8"
    magnetic_position_1 = "3"

    # 20ul tips
    tips_20ul: List[Labware] = [
        ctx.load_labware(
            load_name="opentrons_96_tiprack_20ul",
            location=tips_20ul_position,
            label="20ul tips",
        )
    ]

    # pipettes
    pipette_right: InstrumentContext = ctx.load_instrument(
        instrument_name="p20_single_gen2", mount="right", tip_racks=tips_20ul
    )

    # loaded but unused
    # should be safe, common to forget to comment out or leave in accidentaly
    pipette_left: InstrumentContext = ctx.load_instrument(
        instrument_name="p300_multi_gen2", mount="left"
    )

    # modules
    magnetic_module_1 = ctx.load_module("magnetic module gen2", magnetic_position_1)
    magnetic_module_2 = ctx.load_module("magnetic module gen2", magnetic_position_2)

    # module labware

    mag_plate_1 = magnetic_module_1.load_labware(
        "nest_96_wellplate_100ul_pcr_full_skirt"
    )
    mag_plate_2 = magnetic_module_2.load_labware(
        "nest_96_wellplate_100ul_pcr_full_skirt"
    )

    dye_container: Labware = ctx.load_labware(
        load_name="nest_12_reservoir_15ml",
        location=dye_source_postion,
        label="dye container",
    )

    dye2_source = dye_container.wells_by_name()["A2"]

    for height in range(0, 9):  # 0-8
        magnetic_module_1.engage(height=height)
        magnetic_module_2.engage(height=height)
        ctx.delay(0.3)
    for height in range(7, -1, -1):  # 7-0
        magnetic_module_1.engage(height=height)
        magnetic_module_2.engage(height=height)
        ctx.delay(0.3)
    magnetic_module_1.disengage()
    magnetic_module_2.disengage()

    pipette_right.pick_up_tip()
    pipette_right.aspirate(volume=18, location=dye2_source)
    pipette_right.dispense(volume=18, location=mag_plate_1.well(0))
    pipette_right.blow_out(location=ctx.fixed_trash["A1"])
    pipette_right.aspirate(volume=18, location=dye2_source)
    pipette_right.dispense(volume=18, location=mag_plate_2.well(0))
    pipette_right.drop_tip()

    ctx.delay(10)

    magnetic_module_1.disengage()
    magnetic_module_2.disengage()
