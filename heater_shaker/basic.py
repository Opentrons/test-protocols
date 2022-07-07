metadata = {
    "protocolName": "Heater-shaker test protocol w/ blocking commands",
    "author": "Opentrons <protocols@opentrons.com>",
    "apiLevel": "2.12",
}


def run(context):
    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", "1")

    # Load adapter + labware on module.
    hs_plate = hs_mod.load_labware(
        "opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat"
    )

    tiprack_20ul = [context.load_labware("opentrons_96_tiprack_20ul", 3)]
    p20 = context.load_instrument("p20_single_gen2", "right", tip_racks=tiprack_20ul)

    reservoir = context.load_labware("agilent_1_reservoir_290ml", 5)

    hs_mod.set_and_wait_for_temperature(
        celsius=37
    )  # Waits until H/S is at 37C (37 in min?)

    p20.pick_up_tip()
    p20.aspirate(15, reservoir["A1"])
    p20.dispense(15, hs_plate["A1"])
    p20.drop_tip()

    hs_mod.set_and_wait_for_shake_speed(
        rpm=300
    )  # Waits until H/S has reached 300rpm speed

    context.delay(minutes=1)

    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
