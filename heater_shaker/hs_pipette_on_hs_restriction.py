metadata = {
    "protocolName": "Heater-shaker testing",
    "author": "Opentrons <protocols@opentrons.com>",
    "apiLevel": "2.12",
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
        "opentrons_96_flat_bottom_adapter_nest_wellplate_200ul_flat"
    )
    hs_mod.close_labware_latch()

    # tiprack_300ul = [context.load_labware('opentrons_96_tiprack_300ul', 3)]
    #p20 = context.load_instrument('p300_single', 'right', tip_racks=tiprack_300ul)

    p20rack = [context.load_labware("opentrons_96_tiprack_20ul", "9")]
    p20 = context.load_instrument("p20_single_gen2", "right", tip_racks=p20rack)

    p20.pick_up_tip()
    #p20.touch_tip(hs_plate['A1'])
    p20.move_to(hs_plate.wells_by_name()['A1'].bottom())
    #hs_mod.set_and_wait_for_temperature(celsius=37)  # should work????

    hs_mod.set_and_wait_for_shake_speed(
        rpm=300
    )  # Waits until H/S has reached 300rpm speed