"""."""
from dataclasses import dataclass
from typing import List

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware, Well


@dataclass
class Values:
    """A class to reference with code completion the values we need to set."""

    pipette_model: str
    pipette_mount: str
    destination_labware_name: str
    destination_labware_location: str
    destination_labware_label: str
    dye_source_labware_name: str
    dye_source_labware_location: str
    dye_source_labware_label: str
    dye1_source_well: str
    dye2_source_well: str
    tip_size: str
    tip_name: str
    tip_label: str
    tip_position: str
    dye_volume: int


values: Values = Values(
    pipette_model="p300_single_gen2",
    pipette_mount="right",
    destination_labware_name="nest_96_wellplate_100ul_pcr_full_skirt",
    destination_labware_location="3",
    destination_labware_label="Destination Plate",
    dye_source_labware_name="nest_12_reservoir_15ml",
    dye_source_labware_location="2",
    dye_source_labware_label="Dye Source",
    dye1_source_well="A1",
    dye2_source_well="A2",
    tip_size="300",
    tip_name="opentrons_96_tiprack_300ul",
    tip_label="Opentrons Tips",
    tip_position="1",
    dye_volume=50,
)


metadata = {
    "protocolName": "Opentrons Logo",
    "author": "Opentrons <protocols@opentrons.com>",
    "source": "Protocol Library",
    "apiLevel": "2.12",
}


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    tips: List[Labware] = [
        ctx.load_labware(
            load_name=values.tip_name,
            location=values.tip_position,
            label=values.tip_label,
        )
    ]

    pipette: InstrumentContext = ctx.load_instrument(
        instrument_name=values.pipette_model, mount=values.pipette_mount, tip_racks=tips
    )

    # create plates and pattern list
    destination_plate: Labware = ctx.load_labware(
        load_name=values.destination_labware_name,
        location=values.destination_labware_location,
        label=values.destination_labware_label,
    )

    dye_container: Labware = ctx.load_labware(
        load_name=values.dye_source_labware_name,
        location=values.dye_source_labware_location,
        label=values.dye_source_labware_label,
    )

    # Well Location set-up
    dye1_destination_wells: List[Well] = [
        destination_plate.wells_by_name()["A5"],
        destination_plate.wells_by_name()["A6"],
        destination_plate.wells_by_name()["A8"],
        destination_plate.wells_by_name()["A9"],
        destination_plate.wells_by_name()["B4"],
        destination_plate.wells_by_name()["B10"],
        destination_plate.wells_by_name()["C3"],
        destination_plate.wells_by_name()["C11"],
        destination_plate.wells_by_name()["D3"],
        destination_plate.wells_by_name()["D11"],
        destination_plate.wells_by_name()["E3"],
        destination_plate.wells_by_name()["E11"],
        destination_plate.wells_by_name()["F3"],
        destination_plate.wells_by_name()["F11"],
        destination_plate.wells_by_name()["G4"],
        destination_plate.wells_by_name()["G10"],
        destination_plate.wells_by_name()["H5"],
        destination_plate.wells_by_name()["H6"],
        destination_plate.wells_by_name()["H7"],
        destination_plate.wells_by_name()["H8"],
        destination_plate.wells_by_name()["H9"],
    ]

    dye2_destination_wells: List[Well] = [
        destination_plate.wells_by_name()["C7"],
        destination_plate.wells_by_name()["D6"],
        destination_plate.wells_by_name()["D7"],
        destination_plate.wells_by_name()["D8"],
        destination_plate.wells_by_name()["E5"],
        destination_plate.wells_by_name()["E6"],
        destination_plate.wells_by_name()["E7"],
        destination_plate.wells_by_name()["E8"],
        destination_plate.wells_by_name()["E9"],
        destination_plate.wells_by_name()["F5"],
        destination_plate.wells_by_name()["F6"],
        destination_plate.wells_by_name()["F7"],
        destination_plate.wells_by_name()["F8"],
        destination_plate.wells_by_name()["F9"],
        destination_plate.wells_by_name()["G6"],
        destination_plate.wells_by_name()["G7"],
        destination_plate.wells_by_name()["G8"],
    ]

    # Distribute dye 1
    pipette.pick_up_tip()
    pipette.distribute(
        volume=values.dye_volume,
        source=[dye_container.wells_by_name()[values.dye1_source_well]],
        dest=dye1_destination_wells,
        new_tip="never",
    )

    # Drop the tip used for dye 1
    pipette.drop_tip()

    # Distribute dye 2
    pipette.pick_up_tip()
    pipette.distribute(
        volume=values.dye_volume,
        source=[dye_container.wells_by_name()[values.dye2_source_well]],
        dest=dye2_destination_wells,
        new_tip="never",
    )

    # No need to drop_tip() this is done for us at the end of the protocol
