from opentrons import protocol_api, types

metadata = {"apiLevel": "2.12"}


def run(protocol_api):

    # labware
    plate = protocol_api.load_labware(
        "nest_96_wellplate_100ul_pcr_full_skirt", location="2"
    )
    tiprack = protocol_api.load_labware("opentrons_96_tiprack_300ul", location="1")

    # pipettes
    pipette = protocol_api.load_instrument(
        "p300_single", mount="left", tip_racks=[tiprack]
    )

    # commands
    pipette.pick_up_tip()
    pipette.move_to(plate["A1"].top())
    protocol_api.delay(seconds=10)
    pipette.move_to(plate["A1"].bottom(1), force_direct=True)
    protocol_api.delay(seconds=10)
    pipette.move_to(plate["A1"].top(-2), force_direct=True)
    protocol_api.delay(seconds=10)
    pipette.move_to(plate["A2"].top())
    pipette.return_tip()
