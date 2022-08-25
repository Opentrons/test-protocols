from typing import List

from opentrons import protocol_api
from opentrons.protocol_api.contexts import InstrumentContext
from opentrons.protocol_api.labware import Labware

metadata = {
    "protocolName": "8 channel pipetting Heater-Shaker testing",
    "author": "Opentrons Engineering <engineering@opentrons.com>",
    "source": "Software Testing Team",
    "apiLevel": "2.13",
}


def run(context: protocol_api.ProtocolContext):

    # Load Heater-shaker module
    hs_mod = context.load_module("heaterShakerModuleV1", "3")
    # Load adapter + labware on module.
    hs_plate = hs_mod.load_labware(
        "opentrons_96_pcr_adapter_nest_wellplate_100ul_pcr_full_skirt"
    )

    # 300ul tips
    tips_300ul: List[Labware] = [
        context.load_labware(
            load_name="opentrons_96_tiprack_300ul", location="1", label="300ul tips"
        )
    ]

    pipette_left: InstrumentContext = context.load_instrument(
        instrument_name="p300_multi_gen2", mount="left", tip_racks=tips_300ul
    )

    hs_mod.close_labware_latch()

    pipette_left.pick_up_tip()

    pipette_left.touch_tip(hs_plate["A1"])

    pipette_left.touch_tip(hs_plate["A6"])

    pipette_left.touch_tip(hs_plate["A12"])

    # pipette gets moved out of the way

    hs_mod.set_and_wait_for_shake_speed(rpm=555)

    context.delay(5)

    hs_mod.deactivate_shaker()

    pipette_left.touch_tip(hs_plate["A10"])

    pipette_left.touch_tip(hs_plate["A7"])

    pipette_left.touch_tip(hs_plate["A3"])

    pipette_left.return_tip()
