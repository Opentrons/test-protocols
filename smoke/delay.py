metadata = {"apiLevel": "2.11"}


def run(ctx):
    tiprack1 = ctx.load_labware_by_name("opentrons_96_tiprack_300ul", "5")
    tiprack2 = ctx.load_labware_by_name("opentrons_96_tiprack_300ul", "2")
    tiprack3 = ctx.load_labware("opentrons_96_tiprack_10ul", "3")
    plate1 = ctx.load_labware("corning_96_wellplate_360ul_flat", "9")
    plate2 = ctx.load_labware("corning_96_wellplate_360ul_flat", "1")
    # pip = ctx.load_instrument('p20_single_gen2', mount='left', tip_racks=[tiprack3])

    pip2 = ctx.load_instrument(
        "p300_multi_gen2", mount="left", tip_racks=[tiprack1, tiprack2]
    )
    # thermocycler = ctx.load_module('thermocyclerModuleV1')
    # reaction_plate = thermocycler.load_labware(
    #        'nest_96_wellplate_100ul_pcr_full_skirt')
    # ctx.max_speeds['A'] = 20
    # pip.transfer(10, plate1.wells('A1'), [plate2[well].top() for well in ['A1', 'B1','C1', 'D1','E1', 'F1','G1','H1']])
    pip2.transfer(
        50,
        plate1.wells("A2"),
        [
            plate2[well].bottom()
            for well in ["A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1"]
        ],
    )
    ctx.delay(seconds=30)


# mix behavior
# pip.transfer(50, plate1.wells('A3'), [plate2[well].top() for well in ['A1', 'B1','C1', 'D1','E1', 'F1','G1','H1']])

# #run time = 3 minutes
# 	pip2.pick_up_tip()
# 	pip2.aspirate(50, plate1['A1'])
# 	pip2.drop_tip()
# 	pip2.pick_up_tip()
# 	pip2.aspirate(50, plate1['A2'])
# 	pip2.drop_tip()
