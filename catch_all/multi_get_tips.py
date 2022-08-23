"""Smoke Test 6.0"""
from typing import List, Optional

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware, Well

metadata = {
    "protocolName": "Multi and single pickup tips",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": (
        "Description of the protocol that is longish \n has \n returns and \n emoji 😊 ⬆️ "
    ),
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    # deck positions
    tips_300ul_position = "1"
    dye_source_postion = "2"
    destination_position = "3"

    # 300ul tips
    tips_300ul: List[Labware] = [
        ctx.load_labware(
            load_name="opentrons_96_tiprack_300ul",
            location=tips_300ul_position,
            label="300ul tips",
        )
    ]

    # pipettes
    pipette_right: InstrumentContext = ctx.load_instrument(
        instrument_name="p300_single_gen2", mount="right", tip_racks=tips_300ul
    )

    pipette_left: InstrumentContext = ctx.load_instrument(
        instrument_name="p300_multi_gen2", mount="left", tip_racks=tips_300ul
    )

    # plates
    destination_plate: Labware = ctx.load_labware(
        load_name="nest_96_wellplate_100ul_pcr_full_skirt",
        location=destination_position,
        label="logo destination",
    )

    dye_container: Labware = ctx.load_labware(
        load_name="nest_12_reservoir_15ml",
        location=dye_source_postion,
        label="dye container",
    )

    dye1_source = dye_container.wells_by_name()["A1"]

    # single pipette
    pipette_right.pick_up_tip()
    pipette_right.aspirate(volume=30, location=dye1_source)
    pipette_right.dispense(volume=30, location=destination_plate.wells_by_name()["A1"])
    pipette_right.drop_tip()

    # multi pipette
    pipette_left.pick_up_tip()  # should get from A2 since tips have been used in column 1
    pipette_left.aspirate(volume=75, location=dye1_source)
    pipette_left.dispense(volume=60, location=destination_plate.wells_by_name()["A6"])
    pipette_left.drop_tip()
