import time

metadata = {
    "protocolName": "Deep Plate Heater-Shaker testing",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "apiLevel": "2.13",
}


def run(context):
    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", "3")

    # Load adapter + labware on module. Available labware:
    # - opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat
    # - opentrons_96_pcr_plate_adapter_nest_wellplate_100ul_pcr_full_skirt
    # - opentrons_96_deepwell_adapter_nest_wellplate_2ml_deep
    # - opentrons_flat_plate_adapter_corning_384_wellplate_112ul_flat
    hs_plate = hs_mod.load_labware(
        "opentrons_96_pcr_plate_adapter_nest_wellplate_100ul_pcr_full_skirt"
    )

    tiprack_20ul = [context.load_labware("opentrons_96_tiprack_20ul", 1)]
    p20 = context.load_instrument("p20_single_gen2", "right", tip_racks=tiprack_20ul)

    hs_mod.close_labware_latch()

    # block until temp is reached
    hs_mod.set_and_wait_for_temperature(37)

    start_time = time.monotonic()  # set reference time

    p20.pick_up_tip()
    p20.touch_tip(hs_plate["A1"])
    p20.move_to(hs_plate.wells_by_name()["A1"].bottom())
    p20.move_to(hs_plate.wells_by_name()["H12"].bottom())

    # delay for the difference between now and 30 seconds after the reference time
    context.delay(max(0, start_time + 30 - time.monotonic()))

    # pipette get moved out of the way
    hs_mod.set_and_wait_for_shake_speed(
        rpm=366
    )  # Waits until H/S has reached 366rpm speed

    # shake for 22
    context.delay(22)

    hs_mod.deactivate_shaker()

    p20.aspirate(15, hs_plate["A12"])
    p20.dispense(10, hs_plate["H1"])
    p20.drop_tip()

    hs_mod.deactivate_heater()
