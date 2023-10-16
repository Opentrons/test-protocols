from opentrons.types import Point
import json
import os
import math
from time import sleep
from opentrons import types
import numpy as np

metadata = {
    "protocolName": "Flex Omega HDQ DNA Extraction with Lysis: Cells 96 channel testing",
    "author": "Zach Galluzzo <zachary.galluzzo@opentrons.com>",
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

dry_run = True
HS_SLOT = 1
USE_GRIPPER = True

"""
Slot A1: Tips 1000
Slot A2: Tips 1000 (for elution)
Slot B1: Nest 96 Deep Well (wash2 reservoir-1300 ul  each well)
Slot B2: 
Slot B3: Nest 1 Well Reservoir
Slot C1: Magblock
Slot C2: Nest 96 Deep Well (AL reservoir- 350 ul each well)
Slot C3: Nest 96 Deep Well (wash1 reservoir-700 ul each well)
Slot D1: H-S with Nest 96 Well Deepwell and DW Adapter (180 ul each well)
Slot D2: Nest 96 Deep Well (beads and bind reservoir-440 ul each well)
Slot D3: Temperature module (gen2) with 96 well PCR block and Armadillo 96 well PCR Plate (100 ul 
each well)
"""

# Start protocol
def run(ctx):
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """

    # Same for all HDQ Extractions
    deepwell_type = "nest_96_wellplate_2ml_deep"
    wash_vol = 600
    if not dry_run:
        settling_time = 2
        num_washes = 3
    if dry_run:
        settling_time = 0.5
        num_washes = 1

    h_s = ctx.load_module("heaterShakerModuleV1", HS_SLOT)
    h_s_adapter = h_s.load_adapter("opentrons_96_deep_well_adapter")
    sample_plate = h_s_adapter.load_labware(deepwell_type)
    samples_m = sample_plate.wells()[0]

    # NOTE: MAG BLOCK will be on slot 6

    temp = ctx.load_module("temperature module gen2", "D3")
    tempblock = temp.load_adapter("opentrons_96_well_aluminum_block")
    magblock = ctx.load_module("magneticBlockV1", "C1")
    elutionplate = tempblock.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt")
    waste = (
        ctx.load_labware("nest_1_reservoir_195ml", "B3", "Liquid Waste").wells()[0].top()
    )

    lysis_res = ctx.load_labware(deepwell_type, "C2").wells()[0]
    bind_res = ctx.load_labware(deepwell_type, "D2").wells()[0]
    wash1_res = ctx.load_labware(deepwell_type, "C3").wells()[0]
    wash2_res = ctx.load_labware(deepwell_type, "B1").wells()[0]
    elution_res = elutionplate.wells()[0]

    # Load tips
    tips = ctx.load_labware("opentrons_flex_96_tiprack_1000ul", "A1", adapter="opentrons_flex_96_tiprack_adapter").wells()[0]
    tips1 = ctx.load_labware("opentrons_flex_96_tiprack_1000ul", "A2", adapter="opentrons_flex_96_tiprack_adapter").wells()[0]

    # Differences between sample types
    AL_vol = 250
    sample_vol = 180
    inc_temp = 55
    starting_vol = AL_vol + sample_vol
    binding_buffer_vol = 340
    elution_vol = 100

    # load 96 channel pipette
    pip = ctx.load_instrument("flex_96channel_1000", mount="left")

    pip.flow_rate.aspirate = 50
    pip.flow_rate.dispense = 150
    pip.flow_rate.blow_out = 300

    def resuspend_pellet(vol, plate, reps=3):
        pip.flow_rate.aspirate = 200
        pip.flow_rate.dispense = 300

        loc1 = plate.bottom().move(types.Point(x=1, y=0, z=1))
        loc2 = plate.bottom().move(types.Point(x=0.75, y=0.75, z=1))
        loc3 = plate.bottom().move(types.Point(x=0, y=1, z=1))
        loc4 = plate.bottom().move(types.Point(x=-0.75, y=0.75, z=1))
        loc5 = plate.bottom().move(types.Point(x=-1, y=0, z=1))
        loc6 = plate.bottom().move(types.Point(x=-0.75, y=0 - 0.75, z=1))
        loc7 = plate.bottom().move(types.Point(x=0, y=-1, z=1))
        loc8 = plate.bottom().move(types.Point(x=0.75, y=-0.75, z=1))

        if vol > 1000:
            vol = 1000

        mixvol = vol * 0.9

        for _ in range(reps):
            pip.aspirate(mixvol, loc1)
            pip.dispense(mixvol, loc1)
            pip.aspirate(mixvol, loc2)
            pip.dispense(mixvol, loc2)
            pip.aspirate(mixvol, loc3)
            pip.dispense(mixvol, loc3)
            pip.aspirate(mixvol, loc4)
            pip.dispense(mixvol, loc4)
            pip.aspirate(mixvol, loc5)
            pip.dispense(mixvol, loc5)
            pip.aspirate(mixvol, loc6)
            pip.dispense(mixvol, loc6)
            pip.aspirate(mixvol, loc7)
            pip.dispense(mixvol, loc7)
            pip.aspirate(mixvol, loc8)
            pip.dispense(mixvol, loc8)
            if _ == reps - 1:
                pip.flow_rate.aspirate = 50
                pip.flow_rate.dispense = 30
                pip.aspirate(mixvol, loc8)
                pip.dispense(mixvol, loc8)

        pip.flow_rate.aspirate = 150
        pip.flow_rate.dispense = 200

    def bead_mix(vol, plate, reps=5):
        pip.flow_rate.aspirate = 200
        pip.flow_rate.dispense = 300

        loc1 = plate.bottom().move(types.Point(x=0, y=0, z=1))
        loc2 = plate.bottom().move(types.Point(x=0, y=0, z=8))
        loc3 = plate.bottom().move(types.Point(x=0, y=0, z=16))
        loc4 = plate.bottom().move(types.Point(x=0, y=0, z=24))

        if vol > 1000:
            vol = 1000

        mixvol = vol * 0.9

        for _ in range(reps):
            pip.aspirate(mixvol, loc1)
            pip.dispense(mixvol, loc1)
            pip.aspirate(mixvol, loc1)
            pip.dispense(mixvol, loc2)
            pip.aspirate(mixvol, loc1)
            pip.dispense(mixvol, loc3)
            pip.aspirate(mixvol, loc1)
            pip.dispense(mixvol, loc4)
            if _ == reps - 1:
                pip.flow_rate.aspirate = 50
                pip.flow_rate.dispense = 30
                pip.aspirate(mixvol, loc1)
                pip.dispense(mixvol, loc1)

        pip.flow_rate.aspirate = 150
        pip.flow_rate.dispense = 200

    # Just in case
    h_s.close_labware_latch()

    # Start Protocol

    # Transfer and mix lysis
    pip.pick_up_tip(tips)
    pip.aspirate(AL_vol, lysis_res)
    pip.dispense(AL_vol, samples_m)
    resuspend_pellet(400, samples_m, reps=4 if not dry_run else 1)
    pip.drop_tip(tips)

    # Mix, then heat
    h_s.set_and_wait_for_shake_speed(1800)
    ctx.delay(
        minutes=10 if not dry_run else 0.25,
        msg="Please wait 10 minutes to allow for proper lysis mixing.",
    )

    if not dry_run:
        h_s.set_and_wait_for_temperature(55)
    ctx.delay(
        minutes=10 if not dry_run else 0.25,
        msg="Please allow another 10 minutes of 55C incubation to complete lysis.",
    )

    h_s.deactivate_shaker()

    # Transfer and mix bind&beads
    pip.pick_up_tip(tips)
    bead_mix(binding_buffer_vol, bind_res, reps=4 if not dry_run else 1)
    pip.aspirate(binding_buffer_vol, bind_res)
    pip.dispense(binding_buffer_vol, samples_m)
    bead_mix(binding_buffer_vol + starting_vol, samples_m, reps=4 if not dry_run else 1)
    pip.return_tip()
    pip.home()

    # Shake for binding incubation
    h_s.set_and_wait_for_shake_speed(rpm=1800)
    ctx.delay(
        minutes=10 if not dry_run else 0.25,
        msg="Please allow 10 minutes for the beads to bind the DNA.",
    )

    h_s.deactivate_shaker()

    h_s.open_labware_latch()
    # Transfer plate to magnet
    ctx.move_labware(
        sample_plate,
        magblock,
        use_gripper=USE_GRIPPER,
    )
    h_s.close_labware_latch()

    ctx.delay(
        minutes=settling_time,
        msg="Please wait " + str(settling_time) + " minute(s) for beads to pellet.",
    )

    # Remove Supernatant and move off magnet
    pip.pick_up_tip(tips)
    pip.aspirate(1000, samples_m.bottom(0.3))
    pip.dispense(1000, waste)
    if starting_vol + binding_buffer_vol > 1000:
        pip.aspirate(1000, samples_m.bottom(0.1))
        pip.dispense(1000, waste)
    pip.return_tip()

    # Transfer plate from magnet to H/S
    h_s.open_labware_latch()
    ctx.move_labware(
        sample_plate,
        h_s_adapter,
        use_gripper=USE_GRIPPER,
    )

    h_s.close_labware_latch()

    # Washes
    for i in range(num_washes):
        if i == 0 or i == 1:
            wash_res = wash1_res
        else:
            wash_res = wash2_res

        pip.pick_up_tip(tips)
        pip.aspirate(wash_vol, wash_res)
        pip.dispense(wash_vol, samples_m)
        pip.return_tip()

        h_s.set_and_wait_for_shake_speed(rpm=1800)
        ctx.delay(minutes=5 if not dry_run else 0.25)
        h_s.deactivate_shaker()
        h_s.open_labware_latch()

        # Transfer plate to magnet
        ctx.move_labware(
            sample_plate,
            magblock,
            use_gripper=USE_GRIPPER,
        )

        ctx.delay(
            minutes=settling_time,
            msg="Please wait " + str(settling_time) + " minute(s) for beads to pellet.",
        )

        # Remove Supernatant and move off magnet
        pip.pick_up_tip(tips)
        pip.aspirate(1000, samples_m.bottom(0.3))
        pip.dispense(1000, bind_res.top())
        if wash_vol > 1000:
            pip.aspirate(1000, samples_m.bottom(0.3))
            pip.dispense(1000, bind_res.top())
        pip.return_tip()

        # Transfer plate from magnet to H/S
        ctx.move_labware(
            sample_plate,
            h_s_adapter,
            use_gripper=USE_GRIPPER,
        )
        h_s.close_labware_latch()

    # Dry beads
    if dry_run:
        drybeads = 0.5
    else:
        drybeads = 10
    # Number of minutes you want to dry for
    for beaddry in np.arange(drybeads, 0, -0.5):
        ctx.delay(
            minutes=0.5,
            msg="There are " + str(beaddry) + " minutes left in the drying step.",
        )

    # Elution
    pip.pick_up_tip(tips1)
    pip.aspirate(elution_vol, elution_res)
    pip.dispense(elution_vol, samples_m)
    resuspend_pellet(elution_vol, samples_m, reps=3 if not dry_run else 1)
    pip.return_tip()
    pip.home()

    h_s.set_and_wait_for_shake_speed(rpm=2000)
    ctx.delay(
        minutes=5 if not dry_run else 0.25,
        msg="Please wait 5 minutes to allow dna to elute from beads.",
    )
    h_s.deactivate_shaker()
    h_s.open_labware_latch()

    # Transfer plate to magnet
    ctx.move_labware(
        sample_plate,
        magblock,
        use_gripper=USE_GRIPPER,
    )

    ctx.delay(
        minutes=settling_time,
        msg="Please wait " + str(settling_time) + " minute(s) for beads to pellet.",
    )

    pip.pick_up_tip(tips1)
    pip.aspirate(elution_vol, samples_m)
    pip.dispense(elution_vol, elutionplate.wells()[0])
    pip.return_tip()

    pip.home()
