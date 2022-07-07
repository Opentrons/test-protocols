from opentrons import protocol_api

metadata = {"apiLevel": "2.11"}


def run(protocol: protocol_api.ProtocolContext):
    """."""
    plate = protocol.load_labware("corning_96_wellplate_360ul_flat", 4)
    tiprack_1 = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    p300 = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[tiprack_1])
    p300.pick_up_tip()
    p300.aspirate(200, plate["A1"])
    p300.dispense(50, plate["B1"])
    protocol.comment("example comment")

    for i in range(0, 5):
        protocol.comment(f"A range of comments n={str(i)}")
    protocol.comment("When do I happen?")
    p300.dispense(50, plate["B1"])
    protocol.pause("You must scroll to see me!")
    p300.dispense(50, plate["B1"])  # this is the command to pause before

    for i in range(0, 10):
        protocol.comment(f"A range of comments n={str(i)}")
    protocol.pause("You must scroll to see me!")
    p300.drop_tip()
