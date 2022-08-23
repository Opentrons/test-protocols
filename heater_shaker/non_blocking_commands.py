import time

metadata = {
    "protocolName": "Heater-shaker test protocol w/ non blocking commands",
    "author": "Opentrons <protocols@opentrons.com>",
    "apiLevel": "2.12",
}

SHAKE_TIME_MINUTES = 1


def run(context):
    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", 1)

    # Load adapter + labware on module. Available labware:
    # - opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat
    # - opentrons_96_pcr_plate_adapter_nest_wellplate_100ul_pcr_full_skirt
    # - opentrons_96_deepwell_adapter_nest_wellplate_2ml_deep
    # - opentrons_flat_plate_adapter_corning_384_wellplate_112ul_flat
    hs_plate = hs_mod.load_labware(
        "opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat"
    )
    other_plate = context.load_labware("biorad_96_wellplate_200ul_pcr", 6)

    tiprack_10ul = [context.load_labware("opentrons_96_tiprack_10ul", 3)]
    p20 = context.load_instrument("p20_single_gen2", "right", tip_racks=tiprack_10ul)

    reservoir = context.load_labware("agilent_1_reservoir_290ml", 5)

    hs_mod.set_target_temperature(celsius=40)  # Sets target and moves on. Doesn't wait

    p20.pick_up_tip()
    p20.aspirate(10, reservoir["A1"])
    p20.dispense(10, hs_plate["A1"])
    p20.drop_tip()

    hs_mod.wait_for_temperature()  # Cannot specify a temperature. Waits for the previously set target temperature only

    saved_time = time.time()  # saves seconds since epoch (January 1, 1970, 00:00:00)

    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(
        rpm=500
    )  # Waits until H/S has reached 500rpm speed

    p20.pick_up_tip()
    p20.aspirate(10, reservoir["A1"])
    p20.dispense(10, other_plate["A1"])
    p20.drop_tip()

    context.comment(msg=f"Waiting until shaken for {SHAKE_TIME_MINUTES}min.")

    if not context.is_simulating():
        while (
            time.time() - saved_time < SHAKE_TIME_MINUTES * 60
        ):  # Wait until SHAKE_TIME_MINUTES since saved_time
            time.sleep(1)

    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
