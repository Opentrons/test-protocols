from opentrons import protocol_api

metadata = {
    "protocolName": "Thermocycler status comments",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "description": ("Use all the properties."),
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

    ctx.comment(f"api_version = {str(tc_mod.api_version)}")
    ctx.comment(f"lid_position = {str(tc_mod.lid_position)}")
    ctx.comment(f"lid_target_temperature = {str(tc_mod.lid_target_temperature)}")
    ctx.comment(f"lid_temperature = {str(tc_mod.lid_temperature)}")
    ctx.comment(f"lid_temperature_status = {str(tc_mod.lid_temperature_status)}")
    ctx.comment(f"block_temperature = {str(tc_mod.block_temperature)}")
    ctx.comment(f"block_temperature_status = {tc_mod.block_temperature_status}") # doc says guaranteed string
