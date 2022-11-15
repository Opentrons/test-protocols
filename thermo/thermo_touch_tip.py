from opentrons import protocol_api

metadata = {
    "protocolName": "Thermocycler Touch Tip",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("Use touch tip command on TC."),
    "apiLevel": "2.13",
}

TC_GEN1 = "Thermocycler Module"
TC_GEN2 = "thermocyclerModuleV2"

def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    tc_mod = ctx.load_module(TC_GEN2)
    tc_plate = tc_mod.load_labware(
        "nest_96_wellplate_100ul_pcr_full_skirt"
    )

    tiprack_20ul = [ctx.load_labware("opentrons_96_tiprack_20ul", 3)]
    p20 = ctx.load_instrument("p20_single_gen2", "right", tip_racks=tiprack_20ul)

    # both block and lid
    tc_mod.deactivate()

    tc_mod.close_lid()
    # manually close the lid with the lid with the button
    tc_mod.open_lid() # comment this line out to make sure that there is an error if you try to move to TC with lid closed.

    p20.pick_up_tip()

    p20.touch_tip(tc_plate["A1"])

    p20.touch_tip(tc_plate["A6"])

    p20.touch_tip(tc_plate["A12"])
