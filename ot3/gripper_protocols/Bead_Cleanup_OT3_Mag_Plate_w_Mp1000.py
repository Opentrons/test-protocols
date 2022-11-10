from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Bead Cleanup OT3 Mag Plate w Mp1000',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.13",
}

# SCRIPT SETTINGS
DRYRUN      = 'NO'          # YES or NO, DRYRUN = 'YES' will return tips, skip incubation times, shorten mix, for testing purposes
TIPREUSE    = 'YES'          # YES or NO, Reuses tips during Washes
MAG         = 'MAGPLATE'
TIPMIX      = 'YES'

# PROTOCOL SETTINGS
COLUMNS     = 3             # 1-3
FRAGTIME    = 30            # Minutes, Duration of the Fragmentation Step
PCRCYCLES   = 4             # Amount of Cycles

# PROTOCOL BLOCKS
STEP_AMPURE        = 1
STEP_AMPURESS      = 0

p50_tips  = 0
p1000_tips = 0

MAG_PLATE_SLOT = 2
USE_GRIPPER = True


def run(protocol: protocol_api.ProtocolContext):
    global TIPREUSE
    global DRYRUN
    global p50_tips
    global p1000_tips
    global MAG
    global TIPMIX

    protocol.comment('THIS IS A DRY RUN') if DRYRUN == 'YES' else protocol.comment('THIS IS A REACTION RUN')

    # DECK SETUP AND LABWARE
    protocol.comment('THIS IS A MODULE RUN')
    sample_plate        = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt','1')
    reservoir           = protocol.load_labware('nest_12_reservoir_15ml','3')
    tiprack_1000_1       = protocol.load_labware('opentrons_ot3_96_tiprack_1000ul', '5')
    if TIPREUSE == 'YES':
        protocol.comment("THIS PROTOCOL WILL REUSE TIPS FOR WASHES")

    # REAGENT PLATE

    # RESERVOIR
    AMPure              = reservoir['A1']
    EtOH                = reservoir['A4']
    RSB                 = reservoir['A6']
    Liquid_trash        = reservoir['A11']

    # pipette
    p1000 = protocol.load_instrument("p1000_multi_gen3", "right", tip_racks=[tiprack_1000_1])
    p50 = protocol.load_instrument("p50_single_gen3", "left")

    #tip and sample tracking
    column_1_list = []
    column_2_list = []
    column_3_list = []
    column_4_list = []
    barcodes = []
    if COLUMNS >= 1:
        column_1_list.append('A4')
        column_2_list.append('A12')
        column_3_list.append('A7')
        column_4_list.append('A10')
        barcodes.append('A7')
    if COLUMNS >= 2:
        column_1_list.append('A2')
        column_2_list.append('A5')
        column_3_list.append('A8')
        column_4_list.append('A11')
        barcodes.append('A8')
    if COLUMNS >= 3:
        column_1_list.append('A3')
        column_2_list.append('A6')
        column_3_list.append('A9')
        column_4_list.append('A12')
        barcodes.append('A9')

    def p1000_pick_up_tip():
        global p1000_tips
        if p1000_tips >= 3*12:
            protocol.pause('RESET p1000 TIPS')
            p1000.reset_tipracks()
            p1000_tips = 0
        p1000.pick_up_tip()
        p1000_tips += 1

    def p50_pick_up_tip():
        global p50_tips
        if p50_tips >= 12:
            protocol.pause('RESET p50 TIPS')
            p50.reset_tipracks()
            p50_tips = 0
        p50.pick_up_tip()
        p50_tips += 1

    def p50_reuse_tip(loop):
        global TIPREUSE
        if TIPREUSE == 'NO':
            if p20_tips >= 12:
                protocol.pause('RESET p50 TIPS')
                p50.reset_tipracks()
                p20_tips = 0
            p50.pick_up_tip()
        if TIPREUSE == 'YES':
            if p20_tips <=11:
                p50.pick_up_tip(tiprack_20.wells()[(p20_tips - COLUMNS + loop) * 8])

    def p50_drop_tip(loop):
        global TIPREUSE
        global DRYRUN
        if DRYRUN == 'NO':
            if TIPREUSE == 'YES':
                p50.return_tip()
            else:
                p50.drop_tip()
        else:
                p50.return_tip()

    def p1000_reuse_tip(loop):
        global TIPREUSE
        global p1000_tips
        if TIPREUSE == 'NO':
            if p1000_tips >= 12*3:
                protocol.pause('RESET p1000 TIPS')
                p1000.reset_tipracks()
                p1000_tips = 0
            p1000.pick_up_tip()
            p1000_tips += 1
        if TIPREUSE == 'YES':
            protocol.comment(str(p1000_tips) + ' - ' + str(COLUMNS) + ' + ' + str(loop))
            if (p1000_tips - COLUMNS + loop) <=11:
                p1000.pick_up_tip(tiprack_1000_1.wells()[(p1000_tips - COLUMNS + loop) * 8])
                protocol.comment('tiprack_1000_1 : ' + str((p1000_tips - COLUMNS + loop) * 8))
            elif (p1000_tips - COLUMNS + loop) <=23:
                p1000.pick_up_tip(tiprack_200_2.wells()[(p1000_tips - 12 - COLUMNS + loop) * 8])
                protocol.comment('tiprack_200_2 : ' + str((p1000_tips - 12 - COLUMNS + loop) * 8))
            elif (p1000_tips - COLUMNS + loop) <=35:
                p1000.pick_up_tip(tiprack_200_3.wells()[(p1000_tips - 24 - COLUMNS + loop) * 8])
                protocol.comment('tiprack_200_3 : ' + str((p1000_tips - 24 - COLUMNS + loop) * 8))

    def p1000_drop_tip(loop):
        global TIPREUSE
        global DRYRUN
        if DRYRUN == 'NO':
            if TIPREUSE == 'YES':
                p1000.return_tip()
            else:
                p1000.drop_tip()
        else:
                p1000.return_tip()

    def p1000_move_to(well,pos):
        if MAG == 'MAGPLATE':
                if pos == 'p300_bead_side':
                    p1000.move_to(sample_plate[X].bottom(z=0.2))
                if pos == 'p300_bead_top':
                    p1000.move_to(sample_plate[X].bottom(z=0.2))
                if pos == 'p300_bead_mid':
                    p1000.move_to(sample_plate[X].bottom(z=0.2))
                if pos == 'p300_loc1':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.3 * 0.8, y=1.3 * 0.8, z=-4)))
                if pos == 'p300_loc2':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.3, y=0, z=-4)))
                if pos == 'p300_loc3':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.3, y=0, z=-4)))
        elif MAG == 'MAGMOD':
            if well in ('A1','A3','A5','A7','A9','A11'):
                if pos == 'p300_bead_side':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=-0.50, y=0, z=-7.2)))
                if pos == 'p300_bead_top':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.30, y=0, z=-1)))
                if pos == 'p300_bead_mid':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=0.80, y=0, z=-4)))
                if pos == 'p300_loc1':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.3 * 0.8, y=1.3 * 0.8, z=-4)))
                if pos == 'p300_loc2':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.3, y=0, z=-4)))
                if pos == 'p300_loc3':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=1.3, y=0, z=-4)))
            if well in ('A2','A4','A6','A8','A10','A12'):
                if pos == 'p300_bead_side':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=0.50, y=0, z=-7.2)))
                if pos == 'p300_bead_top':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=-1.30, y=0, z=-1)))
                if pos == 'p300_bead_mid':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=-0.80, y=0, z=-4)))
                if pos == 'p300_loc1':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=-1.3 * 0.8, y=1.3 * 0.8, z=-4)))
                if pos == 'p300_loc2':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=-1.3, y=0, z=-4)))
                if pos == 'p300_loc3':
                    p1000.move_to(sample_plate[X].center().move(types.Point(x=-1.3, y=0, z=-4)))

    def p50_move_to(well,pos):
        if well in ('A1','A3','A5','A7','A9','A11'):
            if pos == 'p20_bead_side':
                p50.move_to(sample_plate[X].center().move(types.Point(x=-0.50, y=0, z=-7.2)))
            if pos == 'p20_bead_top':
                p50.move_to(sample_plate[X].center().move(types.Point(x=1.30, y=0, z=-1)))
            if pos == 'p20_bead_mid':
                p50.move_to(sample_plate[X].center().move(types.Point(x=0.80, y=0, z=-4)))
            if pos == 'p20_loc1':
                p50.move_to(sample_plate[X].center().move(types.Point(x=1.3 * 0.8, y=1.3 * 0.8, z=-4)))
            if pos == 'p20_loc2':
                p50.move_to(sample_plate[X].center().move(types.Point(x=1.3, y=0, z=-4)))
            if pos == 'p20_loc3':
                p50.move_to(sample_plate[X].center().move(types.Point(x=1.3, y=0, z=-4)))
        if well in ('A2','A4','A6','A8','A10','A12'):
            if pos == 'p20_bead_side':
                p50.move_to(sample_plate[X].center().move(types.Point(x=0.50, y=0, z=-7.2)))
            if pos == 'p20_bead_top':
                p50.move_to(sample_plate[X].center().move(types.Point(x=-1.30, y=0, z=-1)))
            if pos == 'p20_bead_mid':
                p50.move_to(sample_plate[X].center().move(types.Point(x=-0.80, y=0, z=-4)))
            if pos == 'p20_loc1':
                p50.move_to(sample_plate[X].center().move(types.Point(x=-1.3 * 0.8, y=1.3 * 0.8, z=-4)))
            if pos == 'p20_loc2':
                p50.move_to(sample_plate[X].center().move(types.Point(x=-1.3, y=0, z=-4)))
            if pos == 'p20_loc3':
                p50.move_to(sample_plate[X].center().move(types.Point(x=-1.3, y=0, z=-4)))

    # commands
    if STEP_AMPURE == 1:
        protocol.comment('==============================================')
        protocol.comment('--> Cleanup 1')
        protocol.comment('==============================================')

        protocol.comment('--> ADDING AMPure (1.8x)')
        AMPureVol = 32.5
        AMPureMixRep = 20 if DRYRUN == 'NO' else 1
        AMPureMixVol = 80
        AMPurePremix = 5 if DRYRUN == 'NO' else 1
        for loop, X in enumerate(column_1_list):
            p1000_pick_up_tip()
            p1000.mix(AMPurePremix, AMPureVol + 10, AMPure.bottom(z=2))
            p1000.aspirate(AMPureVol, AMPure.bottom(z=2), rate=0.25)
            p1000.dispense(AMPureVol / 2, sample_plate[X].bottom(z=2), rate=0.25)
            p1000.default_speed = 5
            p1000.dispense(AMPureVol / 2, sample_plate[X].center(), rate=0.25)
            p1000.move_to(sample_plate[X].center())
            if TIPMIX == 'YES':
                for Mix in range(AMPureMixRep):
                    p1000.aspirate(AMPureMixVol / 2, rate=0.5)
                    p1000.move_to(sample_plate[X].bottom(z=2))
                    p1000.aspirate(AMPureMixVol / 2, rate=0.5)
                    p1000.dispense(AMPureMixVol / 2, rate=0.5)
                    p1000.move_to(sample_plate[X].center())
                    p1000.dispense(AMPureMixVol / 2, rate=0.5)
                    Mix += 1
            p1000.blow_out(sample_plate[X].top(z=1))
            p1000.default_speed = 400
            p1000_drop_tip(loop)
        if TIPMIX != 'YES':
            protocol.pause('MIX PLATE')

#       ============================================================================================
#       GRIPPER MOVE PLATE FROM DECK TO MAG PLATE

        if MAG == 'MAGPLATE':
            protocol.move_labware(
                labware=sample_plate,
                new_location=MAG_PLATE_SLOT,
                use_gripper=USE_GRIPPER,
            )
#       ============================================================================================

        if DRYRUN == 'NO':
            protocol.delay(minutes=3)

        protocol.comment('--> Removing Supernatant')
        RemoveSup = 200
        for loop, X in enumerate(column_1_list):
            p1000_reuse_tip(loop)
            p1000.move_to(sample_plate[X].bottom(z=4))
            p1000.aspirate(RemoveSup - 20, rate=0.25)
            p1000.default_speed = 5
            p1000_move_to(X, 'p300_bead_side')
            protocol.delay(minutes=0.1)
            p1000.aspirate(20, rate=0.2)
            p1000.move_to(sample_plate[X].top(z=2))
            p1000.default_speed = 400
            p1000.dispense(200, Liquid_trash)
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()

        protocol.comment('--> ETOH Wash #1')
        ETOHMaxVol = 150
        for loop, X in enumerate(column_1_list):
            p1000_pick_up_tip()
            p1000.aspirate(ETOHMaxVol, EtOH.bottom(z=2))
            p1000_move_to(X, 'p300_bead_side')
            p1000.dispense(ETOHMaxVol - 50, rate=0.5)
            p1000.move_to(sample_plate[X].center())
            p1000.dispense(50, rate=0.5)
            p1000.move_to(sample_plate[X].top(z=2))
            p1000.default_speed = 5
            p1000.move_to(sample_plate[X].top(z=-2))
            protocol.delay(minutes=0.1)
            p1000.blow_out(sample_plate[X].top(z=-2))
            p1000.default_speed = 400
            p1000_drop_tip(loop)

        protocol.delay(minutes=0.5)

        protocol.comment('--> Remove ETOH Wash #1')
        for loop, X in enumerate(column_1_list):
            p1000_reuse_tip(loop)
            p1000.move_to(sample_plate[X].bottom(4))
            p1000.aspirate(ETOHMaxVol, rate=0.25)
            p1000.default_speed = 5
            p1000_move_to(X, 'p300_bead_side')
            protocol.delay(minutes=0.1)
            p1000.aspirate(200 - ETOHMaxVol, rate=0.25)
            p1000.default_speed = 400
            p1000.dispense(200, Liquid_trash)
            p1000.move_to(Liquid_trash.top(z=5))
            protocol.delay(minutes=0.1)
            p1000.blow_out()
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()

        protocol.comment('--> ETOH Wash #2')
        ETOHMaxVol = 150
        for loop, X in enumerate(column_1_list):
            p1000_pick_up_tip()
            p1000.aspirate(ETOHMaxVol, EtOH.bottom(z=2))
            p1000_move_to(X, 'p300_bead_side')
            p1000.dispense(ETOHMaxVol - 50, rate=0.5)
            p1000.move_to(sample_plate[X].center())
            p1000.dispense(50, rate=0.5)
            p1000.move_to(sample_plate[X].top(z=2))
            p1000.default_speed = 5
            p1000.move_to(sample_plate[X].top(z=-2))
            protocol.delay(minutes=0.1)
            p1000.blow_out(sample_plate[X].top(z=-2))
            p1000.default_speed = 400
            p1000_drop_tip(loop)

        protocol.delay(minutes=0.5)

        protocol.comment('--> Remove ETOH Wash #2')
        for loop, X in enumerate(column_1_list):
            p1000_reuse_tip(loop)
            p1000.move_to(sample_plate[X].bottom(z=4))
            p1000.aspirate(ETOHMaxVol, rate=0.25)
            p1000.default_speed = 5
            p1000_move_to(X, 'p300_bead_side')
            protocol.delay(minutes=0.1)
            p1000.aspirate(200 - ETOHMaxVol, rate=0.25)
            p1000.default_speed = 400
            p1000.dispense(200, Liquid_trash)
            p1000.move_to(Liquid_trash.top(z=5))
            protocol.delay(minutes=0.1)
            p1000.blow_out(Liquid_trash.top(z=5))
            p1000_drop_tip(loop)

        if DRYRUN == 'NO':
            protocol.delay(minutes=2)

        protocol.comment('--> Removing Residual ETOH')
        for loop, X in enumerate(column_1_list):
            p1000_reuse_tip(loop)
            p1000.move_to(sample_plate[X].bottom(z=1))
            p1000.aspirate(20, rate=0.25)
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()

#       ============================================================================================
#       GRIPPER MOVE PLATE FROM MAGNET PLATE TO DECK
        if MAG == 'MAGPLATE':
            protocol.move_labware(
                labware=sample_plate,
                new_location=1,
                use_gripper=USE_GRIPPER,
            )
#       ============================================================================================

        protocol.comment('--> Adding RSB')
        RSBVol = 32 if STEP_AMPURESS == 0 else 52
        RSBMixRep = 5 if DRYRUN == 'NO' else 1
        RSBMixVol = 30 if STEP_AMPURESS == 0 else 50
        for loop, X in enumerate(column_1_list):
            p1000_pick_up_tip()
            p1000.aspirate(RSBVol, RSB.bottom(z=2))
            p1000_move_to(X, 'p300_loc1')
            p1000.dispense(RSBVol / 5, rate=0.75)
            p1000.default_speed = 5
            p1000_move_to(X, 'p300_loc2')
            p1000.dispense(RSBVol / 5, rate=0.75)
            p1000_move_to(X, 'p300_loc3')
            p1000.dispense(RSBVol / 5, rate=0.75)
            p1000_move_to(X, 'p300_loc2')
            p1000.dispense(RSBVol / 5, rate=0.75)
            p1000_move_to(X, 'p300_loc1')
            p1000.dispense(RSBVol / 5, rate=0.75)
            if TIPMIX == 'YES':
                reps = 5
                for x in range(reps):
                    p1000.move_to(sample_plate[X].bottom(z=2))
                    p1000.aspirate(RSBVol, rate=0.5)
                    p1000_move_to(X, 'p300_bead_top')
                    p1000.dispense(RSBVol, rate=1)
                reps = 3
                for x in range(reps):
                    p1000_move_to(X, 'p300_loc2')
                    p1000.mix(RSBMixRep, RSBMixVol)
                    p1000_move_to(X, 'p300_loc1')
                    p1000.mix(RSBMixRep, RSBMixVol)
                    p1000_move_to(X, 'p300_loc2')
                    p1000.mix(RSBMixRep, RSBMixVol)
                    p1000_move_to(X, 'p300_loc3')
                    p1000.mix(RSBMixRep, RSBMixVol)
                p1000.move_to(sample_plate.wells_by_name()[X].bottom(z=2))
                p1000.mix(RSBMixRep, RSBMixVol)
            p1000.move_to(sample_plate.wells_by_name()[X].top())
            protocol.delay(seconds=0.5)
            p1000.move_to(sample_plate.wells_by_name()[X].center())
            p1000.default_speed = 400
            p1000_drop_tip(loop)
        if TIPMIX != 'YES':
            protocol.pause('MIX PLATE')

#       ============================================================================================
#       GRIPPER MOVE PLATE FROM DECK TO MAG PLATE
        if MAG == 'MAGPLATE':
            protocol.move_labware(
                labware=sample_plate,
                new_location=MAG_PLATE_SLOT,
                use_gripper=USE_GRIPPER,
            )
#       ============================================================================================

        if DRYRUN == 'NO':
            protocol.delay(minutes=3)

        protocol.comment('--> Transferring Supernatant')
        TransferSup = 30 if STEP_AMPURESS == 0 else 50
        for loop, X in enumerate(column_1_list):
            Y = 'A5'
            p1000_reuse_tip(loop)
            p1000.move_to(sample_plate[X].bottom(z=2))
            p1000.aspirate(TransferSup, rate=0.25)
            if STEP_AMPURESS == 0:
                p1000.dispense(TransferSup + 5, sample_plate[column_2_list[loop]].bottom(z=2))
            else:
                p1000.dispense(TransferSup + 5, sample_plate[column_4_list[loop]].bottom(z=2))
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
