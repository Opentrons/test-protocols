from opentrons import protocol_api

metadata = {
    "protocolName": "Thermocycler lid and block commands",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": "Simple protocol with just a profile.",
    "apiLevel": "2.13",
}

TC_GEN1 = "Thermocycler Module"
TC_GEN2 = "thermocyclerModuleV2"

def run(ctx: protocol_api.ProtocolContext) -> None:
    """This method is run by the protocol engine."""

    tc_mod = ctx.load_module(TC_GEN1)
    tc_plate = tc_mod.load_labware(
        "nest_96_wellplate_100ul_pcr_full_skirt"
    )

    profile = [
        {"temperature": 37, "hold_time_seconds": 10},
        {"temperature": 35, "hold_time_seconds": 10},
    ]

    tc_mod.execute_profile(
        steps=profile, repetitions=1, block_max_volume=30
    )

    # both block and lid
    tc_mod.deactivate()

    tc_mod.open_lid()

    tc_mod.set_lid_temperature(37)

    tc_mod.set_block_temperature(26)
    
    tc_mod.set_block_temperature(28, hold_time_seconds=15, block_max_volume=50)

    tc_mod.set_block_temperature(28, hold_time_seconds=1, hold_time_minutes=1)

    tc_mod.deactivate_lid()

    tc_mod.deactivate_block()
