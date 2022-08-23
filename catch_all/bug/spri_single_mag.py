"""OPENTRONS."""
# from opentrons.types import Point
# import json
# import os
import math
import threading
from time import sleep
from opentrons import types


metadata = {
    'protocolName': '8 Samples SPRI Bead Purification, Size Selection',
    'author': 'Opentrons <protocols@opentrons.com>',
    'apiLevel': '2.11'
}


"""
Here is where you can modify the magnetic module engage height:
"""
TEST_MODE = True
flash = True
mag_height = 9.5  # for custom labware sitting on mag modules
# Definitions for deck light flashing


class CancellationToken:
    """FLASH SETUP."""

    def __init__(self):
        """FLASH SETUP."""
        self.is_continued = False

    def set_true(self):
        """FLASH SETUP."""
        self.is_continued = True

    def set_false(self):
        """FLASH SETUP."""
        self.is_continued = False


def turn_on_blinking_notification(hardware, pause):
    """FLASH SETUP."""
    while pause.is_continued:
        hardware.set_lights(rails=True)
        sleep(1)
        hardware.set_lights(rails=False)
        sleep(1)


def create_thread(ctx, cancel_token):
    """FLASH SETUP."""
    t1 = threading.Thread(target=turn_on_blinking_notification,
                          args=(ctx._hw_manager.hardware, cancel_token))
    t1.start()
    return t1


# Start protocol
def run(ctx):
    """PROTOCOL."""
    # Setup for flashing lights notification to empty trash
    cancellationToken = CancellationToken()

    # [num_samples, deepwell_type, res_type, starting_vol, binding_buffer_vol,
    #  wash1_vol, wash2_vol, wash3_vol, elution_vol, mix_reps, settling_time,
    #  park_tips, tip_track, flash, p300_mount] = get_values(  # noqa: F821
    #     'num_samples', 'deepwell_type', 'res_type', 'starting_vol',
    #     'binding_buffer_vol', 'wash1_vol', 'wash2_vol', 'wash3_vol',
    #     'elution_vol', 'mix_reps', 'settling_time', 'park_tips', 'tip_track',
    #     'flash', 'p300_mount')

    # Testing variables/always useful ones
    size_selection = True
    num_samples = 8
    num_cols = math.ceil(num_samples/8)
    flash = True
    p300_mount = 'left'

    # Drop Down Variables for Testing
    vol_start = 50  # volume of starting well
    bead_ratio_1 = 0.6  # ratio of SPRI by volume
    bead_ratio_2 = 0.8
    vol_trans = 75
    air_dry_time = 10
    incubation_delay_time = 5
    bead_delay_time = 5  # minutes real run, seconds for test run
    elution_vol = 50
    elution_time = 10
    vol_final_plate = 50

    # Math and Calculations
    vol_bead_add_1 = vol_start*bead_ratio_1
    vol_post_add_1 = vol_bead_add_1+vol_start
    vol_bead_add_2 = (bead_ratio_2*vol_start*(vol_trans/vol_post_add_1))\
        - vol_bead_add_1

    """Above vol_bead_add_2 equation came from Illumina website. Source here:
        https://support.illumina.com/bulletins/2020/07/library-size-selection-
        using-sample-purification-beads.html"""

    # Deprecated calculations below
    # PEG_conc_correction = (vol_trans_post_SPRI_1/vol_total)*bead_ratio
    # PEG_vol_correction = round(PEG_conc_correction*vol_total, 1)

    supernatant_headspeed_modulator = 10

    if p300_mount == 'right':
        p20_mount = 'left'
    else:
        p20_mount = 'right'
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    magdeck_1 = ctx.load_module('magnetic module gen2', '7')
    magdeck_1.disengage()
    magplate_1 = magdeck_1.load_labware('customadapter_96_wellplate_200ul',
                                        'sample plate')
    magplate_2 = ctx.load_labware('customadapter_96_wellplate_200ul', '6')

    elutionplate = ctx.load_labware(
                'thermo_96_aluminumblock_200ul',
                '3')
    waste = ctx.load_labware('nest_1_reservoir_195ml', '4',
                             'Liquid Waste').wells()[0].top()
    res1 = ctx.load_labware('nest_12_reservoir_15ml', '5',
                            'reagent reservoir 1')
    tips300 = [ctx.load_labware('opentrons_96_filtertiprack_200ul', slot,
                                '200µl filtertiprack')
               for slot in ['2', '8', '9', '10', '11']]
    tips20 = [ctx.load_labware('opentrons_96_filtertiprack_200ul', slot,
                               '20µl filtertiprack')
              for slot in ['1']]

    parking_spots = [column for column in tips300[0].rows()[0][:num_cols]]
    parking_spots_2 = [column for column in tips300[1].rows()[0][:num_cols]]

    sample_loc_1 = magplate_1.rows()[0][:num_cols]  # where samples start
    sample_dest_1 = magplate_2.rows()[0][:num_cols]  # where first super goes
    sample_dest_2 = elutionplate.rows()[0][:num_cols]  # where final samples go

    bead_well = res1.wells()[0]
    # PEG = res1.wells()[1]
    etoh_1_wells = res1.wells()[1:3]  # 10mL in each, 6 columns per well
    etoh_2_wells = res1.wells()[3:5]  # 10mL in each, 6 columns per well
    elution_solution = res1.wells()[-1]

    # load P300M pipette
    m300 = ctx.load_instrument(
        'p300_multi_gen2', p300_mount, tip_racks=tips300)
    m20 = ctx.load_instrument('p20_multi_gen2', p20_mount, tip_racks=tips20)

    ctx.max_speeds['Z'] = 400
    ctx.max_speeds['A'] = 400
    ctx.max_speeds['X'] = 400
    ctx.max_speeds['Y'] = 400

    # Custom Functions
    def bead_mixing(well, pip, mvol, reps=10):
        """bead_mixing."""
        """
        'bead_mixing' will mix liquid that contains beads. This will be done by
        aspirating from the middle of the well & dispensing from the bottom to
        mix the beads with the other liquids as much as possible. Aspiration &
        dispensing will also be reversed to ensure proper mixing.
        param well: The current well that the mixing will occur in.
        param pip: The pipet that is currently attached/ being used.
        param mvol: The volume that is transferred before the mixing steps.
        param reps: The number of mix repetitions that should occur. Note~
        During each mix rep, there are 2 cycles of aspirating from bottom,
        dispensing at the top and 2 cycles of aspirating from middle,
        dispensing at the bottom
        """
        vol = mvol * .9

        pip.move_to(well.center())
        pip.flow_rate.aspirate = 200
        pip.flow_rate.dispense = 300
        for _ in range(reps):
            pip.aspirate(vol, well.bottom(1))
            pip.dispense(vol, well.bottom(5))
            pip.aspirate(vol, well.bottom(5))
            pip.dispense(vol, well.bottom(1))
        pip.flow_rate.aspirate = 150
        pip.flow_rate.aspirate = 300
    # Begin Protocol

    # bead  addition 1
    for i, dest in enumerate(sample_loc_1):
        if vol_bead_add_1 > 15:
            pip = m300
        else:
            pip = m20
        pip.pick_up_tip()
        if i == 0:
            bead_mixing(bead_well, pip, 20, reps=5)
            pip.aspirate(5, bead_well.top())
        pip.aspirate(vol_bead_add_1, bead_well)
        pip.move_to(dest.top())
        pip.dispense(pip.current_volume, dest)
        bead_mixing(dest, pip, vol_bead_add_1, reps=5)
        pip.aspirate(5, dest.top())
        pip.drop_tip()

    # 5 Minute Incubation
    if TEST_MODE:
        ctx.delay(seconds=incubation_delay_time)
    else:
        ctx.delay(minutes=incubation_delay_time)

    # Magnet engage
    magdeck_1.engage(height_from_base=mag_height)
    if TEST_MODE:
        ctx.delay(seconds=bead_delay_time)
    else:
        ctx.delay(minutes=bead_delay_time)

    # Move supernatant to new plate (this is everything under a certain size)
    for src, dest in zip(sample_loc_1, sample_dest_1):
        side = -1 if i % 2 == 0 else 1
        m300.pick_up_tip()
        m300.aspirate(10, src.top())  # extra air for full liquid dispense
        ctx.max_speeds['Z'] /= supernatant_headspeed_modulator
        ctx.max_speeds['A'] /= supernatant_headspeed_modulator
        m300.aspirate(75, src.bottom().move(types.Point(x=side,
                                                        y=0, z=0.2)))
        m300.aspirate(10, src.top())
        ctx.max_speeds['Z'] *= supernatant_headspeed_modulator
        ctx.max_speeds['A'] *= supernatant_headspeed_modulator
        m300.dispense(10, dest.top())
        m300.dispense(m300.current_volume, dest)
        m300.aspirate(20, dest.top())  # suck in droplets before drop_tip
        m300.drop_tip()

    magdeck_1.disengage()
    # samples are now in slot 6's mag plate, aka magdeck_2

    # Add second bead volume (this binds things above a certain size but lower
    # than the previous sizes selected!)
    # bead addition 2
    for i, dest in enumerate(sample_dest_1):
        if vol_bead_add_1 > 15:
            pip = m300
        else:
            pip = m20
        pip.pick_up_tip()
        if i == 0:
            bead_mixing(bead_well, pip, 20, reps=5)
            pip.aspirate(5, bead_well.top(1))
        pip.aspirate(vol_bead_add_2, bead_well)
        pip.dispense(pip.current_volume, dest)
        bead_mixing(dest, pip, vol_bead_add_2, reps=5)
        pip.aspirate(5, dest.top())
        pip.drop_tip()

    # 5 minute incubation for the new beads to help out
    if TEST_MODE:
        ctx.delay(seconds=incubation_delay_time)
    else:
        ctx.delay(minutes=incubation_delay_time)

    # Engage magnet 2
    # magdeck_2.engage()
    if TEST_MODE:
        ctx.delay(seconds=bead_delay_time)
    else:
        ctx.delay(minutes=bead_delay_time)

    # Empty trash warning
    if flash:
        if not ctx._hw_manager.hardware.is_simulator:
            cancellationToken.set_true()
        thread = create_thread(ctx, cancellationToken)
    m300.home()
    ctx.pause('Please Empty Trash')
    ctx.home()  # home before continuing with protocol
    if flash:
        cancellationToken.set_false()  # stop light flashing after home
        thread.join()
    ctx.set_rail_lights(True)

    # Trash Super, leaving the bead-bound base pairs of a specific size range!
    for src in sample_dest_1:
        side = -1 if i % 2 == 0 else 1
        m300.pick_up_tip()
        m300.aspirate(10, src.top())  # extra air for full liquid dispense
        ctx.max_speeds['Z'] /= supernatant_headspeed_modulator
        ctx.max_speeds['A'] /= supernatant_headspeed_modulator
        m300.aspirate(75+vol_bead_add_2,
                      src.bottom().move(types.Point(x=side,
                                                    y=0, z=0.2)))
        m300.aspirate(10, src.top())  # air gap
        ctx.max_speeds['Z'] *= supernatant_headspeed_modulator
        ctx.max_speeds['A'] *= supernatant_headspeed_modulator
        m300.dispense(10, waste)
        m300.dispense(m300.current_volume, dest)
        m300.aspirate(20, waste)  # suck in droplets before drop_tip
        m300.drop_tip()
    # magdeck_2.disengage()

    # EtOH Wash 1
    for i, (dest, park_loc) in enumerate(zip(sample_dest_1,
                                             parking_spots)):
        m300.pick_up_tip()
        m300.move_to(src.top())
        m300.aspirate(200, etoh_1_wells[i//6])
        m300.dispense(200, dest.top(-1))
        m300.drop_tip(park_loc)

    # Mag 2 Engage
    # magdeck_2.engage()
    if TEST_MODE:
        ctx.delay(seconds=bead_delay_time)
    else:
        ctx.delay(minutes=bead_delay_time)

    # Remove EtOH wash 1
    for src, park_loc in zip(sample_dest_1, parking_spots):
        side = -1 if i % 2 == 0 else 1
        m300.pick_up_tip(park_loc)
        ctx.max_speeds['Z'] /= supernatant_headspeed_modulator
        ctx.max_speeds['A'] /= supernatant_headspeed_modulator
        m300.aspirate(200,
                      src.bottom().move(types.Point(x=side,
                                                    y=0, z=0.2)))
        ctx.max_speeds['Z'] *= supernatant_headspeed_modulator
        ctx.max_speeds['A'] *= supernatant_headspeed_modulator
        m300.dispense(200, waste)
        m300.aspirate(20, waste)  # suck in droplets before drop_tip
        m300.drop_tip(park_loc)

    # magdeck_2.disengage()

    # EtOH wash 2
    for i, (dest, park_loc) in enumerate(zip(sample_dest_1,
                                             parking_spots)):
        m300.pick_up_tip(park_loc)
        m300.move_to(src.top())
        m300.aspirate(200, etoh_2_wells[i//6])
        m300.dispense(200, dest.top(-1))
        m300.drop_tip(park_loc)

    # magdeck_2.engage()
    if TEST_MODE:
        ctx.delay(seconds=bead_delay_time)
    else:
        ctx.delay(minutes=bead_delay_time)

    # Remove EtOH wash 2
    for src, park_loc in zip(sample_dest_1, parking_spots):
        side = -1 if i % 2 == 0 else 1
        m300.pick_up_tip(park_loc)
        ctx.max_speeds['Z'] /= supernatant_headspeed_modulator
        ctx.max_speeds['A'] /= supernatant_headspeed_modulator
        m300.aspirate(200,
                      src.bottom().move(types.Point(x=side,
                                                    y=0, z=0.2)))
        ctx.max_speeds['Z'] *= supernatant_headspeed_modulator
        ctx.max_speeds['A'] *= supernatant_headspeed_modulator
        m300.dispense(200, waste)
        m300.aspirate(20, waste)  # suck in droplets before drop_tip
        m300.drop_tip()

    # magdeck_2.disengage()
    # Air dry

    if TEST_MODE:
        ctx.delay(seconds=air_dry_time)
    else:
        ctx.delay(minutes=air_dry_time)
    # N.B. Tips run out here!
    if flash:
        if not ctx._hw_manager.hardware.is_simulator:
            cancellationToken.set_true()
        thread = create_thread(ctx, cancellationToken)
    m300.home()
    ctx.pause('Please Refill Tip Boxes in Slot 2 then Empty Trash'
              'Press Resume When Finished')
    ctx.home()  # home before continuing with protocol
    if flash:
        cancellationToken.set_false()  # stop light flashing after home
        thread.join()
    ctx.set_rail_lights(True)
    # ctx.pause()
    m300.reset_tipracks()
    # Elute from beads!

    for dest, park_loc in zip(sample_dest_1, parking_spots_2):
        m300.pick_up_tip()
        m300.aspirate(elution_vol, elution_solution)
        m300.dispense(m300.current_volume, dest)
        bead_mixing(dest, m300, 50, reps=5)
        m300.aspirate(20, dest.top())
        m300.drop_tip(park_loc)

    if TEST_MODE:
        ctx.delay(seconds=elution_time)
    else:
        ctx.delay(minutes=elution_time)

    # Mag deck 2 engage

    # magdeck_2.engage()

    if TEST_MODE:
        ctx.delay(seconds=bead_delay_time)
    else:
        ctx.delay(minutes=bead_delay_time)

    # move elution solution to new, final plate
    for src, dest, park_loc in zip(sample_dest_1, sample_dest_2,
                                   parking_spots_2):
        side = -1 if i % 2 == 0 else 1
        m300.pick_up_tip(park_loc)
        ctx.max_speeds['Z'] /= supernatant_headspeed_modulator
        ctx.max_speeds['A'] /= supernatant_headspeed_modulator
        m300.aspirate(vol_final_plate,
                      src.bottom().move(types.Point(x=side,
                                                    y=0, z=0.2)))
        ctx.max_speeds['Z'] *= supernatant_headspeed_modulator
        ctx.max_speeds['A'] *= supernatant_headspeed_modulator
        m300.dispense(m300.current_volume, dest)
        m300.aspirate(20, dest)  # suck in droplets before drop_tip
        m300.drop_tip(park_loc)
