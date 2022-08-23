metadata = {
    "protocolName": "Heater-shaker test protocol w/ blocking commands",
    "author": "Opentrons <protocols@opentrons.com>",
    "apiLevel": "2.12",
}


def run(context):
    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", "1")

    # Load adapter + labware on module. Available labware:
    # - opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat
    # - opentrons_96_pcr_plate_adapter_nest_wellplate_100ul_pcr_full_skirt
    # - opentrons_96_deepwell_adapter_nest_wellplate_2ml_deep
    # - opentrons_flat_plate_adapter_corning_384_wellplate_112ul_flat
    hs_plate = hs_mod.load_labware(
        "opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat"
    )

    # tiprack_300ul = [context.load_labware('opentrons_96_tiprack_300ul', 3)]
    # p20 = context.load_instrument('p300_single', 'right', tip_racks=tiprack_300ul)

    p10rack = [context.load_labware("opentrons_96_tiprack_10ul", "3")]
    p20 = context.load_instrument("p20_single_gen2", "right", tip_racks=p10rack)
    reservoir = context.load_labware("agilent_1_reservoir_290ml", 5)

    hs_mod.open_labware_latch()

    hs_mod.set_and_wait_for_temperature(celsius=80)  # Waits until H/S is at 80C

    p20.pick_up_tip()
    p20.aspirate(10, reservoir["A1"])
    p20.dispense(10, hs_plate["A1"])
    p20.drop_tip()

    hs_mod.close_labware_latch()
    hs_mod.set_and_wait_for_shake_speed(
        rpm=500
    )  # Waits until H/S has reached 500rpm speed

    context.delay(minutes=1)

    hs_mod.deactivate_shaker()
    hs_mod.deactivate_heater()
