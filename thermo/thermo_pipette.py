from opentrons import protocol_api

metadata = {
    "protocolName": "Thermocycler Pipette While Heating",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": "Pipette into a block holding a temp.",
    "apiLevel": "2.13",
}

TC_GEN1 = "Thermocycler Module"
TC_GEN2 = "thermocyclerModuleV2"


def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    tc_mod = ctx.load_module(TC_GEN2)
    tc_plate = tc_mod.load_labware("nest_96_wellplate_100ul_pcr_full_skirt")

    tiprack_20ul = [ctx.load_labware("opentrons_96_tiprack_20ul", 3)]
    p20 = ctx.load_instrument("p20_single_gen2", "right", tip_racks=tiprack_20ul)

    # 300ul tips
    tips_300ul = [
        ctx.load_labware(
            load_name="opentrons_96_tiprack_300ul",
            location=1,
            label="300ul tips",
        )
    ]

    pipette_left = ctx.load_instrument(
        instrument_name="p300_multi_gen2", mount="left", tip_racks=tips_300ul
    )

    tc_mod.set_block_temperature(40)

    dye_container = ctx.load_labware(
        load_name="nest_12_reservoir_15ml",
        location=2,
        label="dye container",
    )

    dye1_source = dye_container.wells_by_name()["A1"]

    # single pipette
    p20.pick_up_tip()
    p20.aspirate(volume=18, location=dye1_source)
    p20.dispense(volume=18, location=tc_plate.wells_by_name()["A1"])
    p20.drop_tip()

    # multi pipette
    pipette_left.pick_up_tip()
    pipette_left.aspirate(volume=75, location=dye1_source)
    pipette_left.dispense(volume=60, location=tc_plate.wells_by_name()["A6"])
    pipette_left.drop_tip()
