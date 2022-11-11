from opentrons.types import Point
import json
import os
import math
import threading
from time import sleep
from opentrons import types
import numpy as np
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#####################################
# ____ Initial Deck setup _____
# Slot 1: Temperature Module
# Slot 2: nest_12_reservoir_15ml
# Slot 3: nest_12_reservoir_15ml
# Slot 4: opentrons_ot3_96_tiprack_200ul
# Slot 5: opentrons_ot3_96_tiprack_1000ul
# Slot 6: empty
# Slot 7: opentrons_ot3_96_tiprack_1000ul
# Slot 8: opentrons_ot3_96_tiprack_1000ul
# Slot 9: nest_1_reservoir_195ml (Liquid waste reservoir)
# Slot 10: Heater-Shaker
# Slot 11: opentrons_ot3_96_tiprack_1000ul

metadata = {
    'protocolName': 'Zymo Magbead RNA Extraction with Lysis: Bacteria',
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>',
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.13",
}

MAG_PLATE_SLOT = 6
USE_GRIPPER = True

"""
Here is where you can modify the magnetic module engage height:
"""
whichwash = 1
tip1k = 0
tip200 = 0
drop_count = 0

# Start protocol
def run(ctx):
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    #Protocol Parameters
    num_samples = 8
    deepwell_type = "nest_96_wellplate_2ml_deep"
    res_type = "nest_12_reservoir_15ml"
    settling_time = 3
    lysis_vol = 200
    binding_buffer_vol = 430 #Beads+Binding
    wash_vol = stop_vol = 500
    dnase_vol = 50
    elution_vol = 110
    starting_vol= 400 #This is sample volume (200 in shield) + lysis volume

    h_s = ctx.load_module('heaterShakerModuleV1','10')
    sample_deepwell_plate = h_s.load_labware(deepwell_type)
    h_s.close_labware_latch()
    tempdeck = ctx.load_module('Temperature Module Gen2','1')
    tempdeck.set_temperature(4)
    elutionplate = tempdeck.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul')
    waste = ctx.load_labware('nest_1_reservoir_195ml', '9',
                             'Liquid Waste').wells()[0].top()
    res1 = ctx.load_labware(res_type, '2', 'reagent reservoir 1')
    res2 = ctx.load_labware(res_type, '3', 'reagent reservoir 2')
    num_cols = math.ceil(num_samples/8)
    
    #Load tips and combine all similar boxes
    t200 = ctx.load_labware('opentrons_ot3_96_tiprack_200ul', '4')
    t1000 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '5')
    t1001 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '7')
    t1002 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '8')
    t1003 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '11')
    t1k = [*t1000.wells(),*t1001.wells(),*t1002.wells(),*t1003.wells()]
    
    # load instruments
    m1000 = ctx.load_instrument('p1000_multi_gen3', 'left')
    m200 = ctx.load_instrument('p1000_multi_gen3', 'right')

    """
    Here is where you can define the locations of your reagents.
    """
    binding_buffer = res1.wells()[0]
    elution_solution = res1.wells()[-1]
    lysis_ = res1.wells()[4:6]
    dnase1 = res1.wells()[1]
    stopreaction = res1.wells()[2:4]
    wash1 = res2.wells()[:2]
    wash2 = res2.wells()[2:4]
    wash3 = res2.wells()[4:6]
    wash4 = res2.wells()[6:8]
    wash5 = res2.wells()[8:10]
    wash6 = res2.wells()[10:]

    elutionplate_row_0 = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12']
    elution_samples_m = elutionplate_row_0[:num_cols]            # elutionplate.rows()[0][:num_cols]

    m200.flow_rate.aspirate = 50
    m200.flow_rate.dispense = 150
    m200.flow_rate.blow_out = 300

    m1000.flow_rate.aspirate = 50
    m1000.flow_rate.dispense = 150
    m1000.flow_rate.blow_out = 300

    def tiptrack(pip, tipbox):
        global tip1k
        global tip200
        global drop_count
        if pip == m1000:
            pip.pick_up_tip(tipbox[int(tip1k)])
            tip1k = tip1k + 8
        if pip == m200:
            pip.pick_up_tip(tipbox[int(tip200)])
            tip200 = tip200 + 8
        drop_count = drop_count + 8
        if drop_count >= 150:
            drop_count = 0
            ctx.pause("Please empty the waste bin of all the tips before continuing.")

    def remove_supernatant(vol):
        m1000.flow_rate.aspirate = 30
        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(sample_m):
            tiptrack(m1000,tips)
            loc = m.bottom(0.5)
            for _ in range(num_trans):
                # if m1000.current_volume > 0:        # TODO: current volume not implemented
                #     # void air gap if necessary
                #     m1000.dispense(m1000.current_volume, m.top())
                m1000.blow_out(m.top())           # TODO: remove this
                m1000.move_to(m.center())
                m1000.transfer(vol_per_trans, loc, waste, new_tip='never',
                              air_gap=20)
                m1000.blow_out(waste)
                m1000.air_gap(20)
            m1000.drop_tip()
        m1000.flow_rate.aspirate = 150

        h_s.open_labware_latch()
        # grip.move(deepwell_type,magnet,h_s)
        ctx.move_labware(
            labware=sample_deepwell_plate,  # plate that is on mag plate
            new_location=h_s,
            use_gripper=USE_GRIPPER,
        )
        h_s.close_labware_latch()

    def mixing(well, pip, mvol, reps=5):
        """
        Likely Unecessary with new magnet
        'mixing' will forcefully dispense liquid over the pellet after
        the magdeck engage in order to more thoroughly resuspend the pellet.
        param well: The current well that the resuspension will occur in.
        param pip: The pipet that is currently attached/ being used.
        param mvol: The volume that is transferred before the mixing steps.
        param reps: The number of mix repetitions that should occur. Note~
        During each mix rep, there are 2 cycles of aspirating from center,
        dispensing at the top and 2 cycles of aspirating from center,
        dispensing at the bottom (5 mixes total)
        

        rightLeft = int(str(well).split(' ')[0][1:]) % 2
        
        'rightLeft' will determine which value to use in the list of 'top' and
        'bottom' (below), based on the column of the 'well' used.
        In the case that an Even column is used, the first value of 'top' and
        'bottom' will be used, otherwise, the second value of each will be used.
        
        center = well.bottom().move(types.Point(x=0,y=0,z=2))
        top = [
            well.bottom().move(types.Point(x=-3,y=3,z=2)),
            well.bottom().move(types.Point(x=3,y=3,z=2))
        ]
        bottom = [
            well.bottom().move(types.Point(x=-3,y=-3,z=2)),
            well.bottom().move(types.Point(x=3,y=-3,z=2))
        ]

        pip.flow_rate.dispense = 500
        pip.flow_rate.aspirate = 150

        mix_vol = 0.9 * mvol

        pip.move_to(center)
        for x in range(reps):
            for _ in range(2):
                pip.aspirate(mix_vol, center)
                pip.dispense(mix_vol, top[rightLeft])
            for _ in range(2):
                pip.aspirate(mix_vol, center)
                pip.dispense(mix_vol, bottom[rightLeft])
            if x == reps-1:
                pip.flow_rate.dispense = 10
                pip.aspirate(mix_vol, center)
                pip.dispense(mix_vol, center)
                pip.blow_out(center)
                pip.flow_rate.dispense = 150
                pip.flow_rate.aspirate = 50
        """

    def blink():
        for i in range(3):
            ctx.set_rail_lights(True)           # Not implemented in engine core
            ctx.delay(minutes=0.01666667)
            ctx.set_rail_lights(False)          # Not implemented in engine core
            ctx.delay(minutes=0.01666667)

    def mixing(well, pip, mvol, reps=8):
        """
        'mixing' will mix liquid that contains beads. This will be done by
        aspirating from the bottom of the well and dispensing from the top as to
        mix the beads with the other liquids as much as possible. Aspiration and
        dispensing will also be reversed for a short to to ensure maximal mixing.
        param well: The current well that the mixing will occur in.
        param pip: The pipet that is currently attached/ being used.
        param mvol: The volume that is transferred before the mixing steps.
        param reps: The number of mix repetitions that should occur. Note~
        During each mix rep, there are 2 cycles of aspirating from bottom,
        dispensing at the top and 2 cycles of aspirating from middle,
        dispensing at the bottom
        """
        center = well.top().move(types.Point(x=0,y=0,z=5))
        aspbot = well.bottom(3)
        asptop = well.bottom(10)
        disbot = well.bottom(5)
        distop = well.top()

        vol = mvol * .9

        pip.move_to(center)
        for _ in range(reps):
            pip.aspirate(vol,aspbot)
            pip.dispense(vol,distop)
            pip.aspirate(vol,asptop)
            pip.dispense(vol,disbot)
            if _ == reps-1:
                pip.flow_rate.aspirate = 20
                pip.flow_rate.dispense = 10
                pip.aspirate(vol,aspbot)
                pip.dispense(vol,aspbot)

        pip.flow_rate.aspirate = 50
        pip.flow_rate.dispense = 150

    def lysis(vol, source):
        num_transfers = math.ceil(vol/980)
        for i in range(num_cols):
            tiptrack(m1000, t1k)
            src = source[i//len(source)]
            tvol = vol/num_transfers
            for t in range(num_transfers):
                m1000.aspirate(tvol,src.bottom(1))
                # m1000.dispense(m1000.current_volume,sample_m[i].top(-3))
                m1000.blow_out(sample_m[i].top(-3))     # TODO: remove this
                if t == num_transfers-1:
                    mixing(sample_m[i],m1000,starting_vol,reps=8)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=2000)
        ctx.delay(minutes=2,msg='Please wait 2 minutes while the lysis buffer mixes with the sample.')
        h_s.deactivate_shaker()

    def bind(vol):
        """
        `bind` will perform magnetic bead binding on each sample in the
        deepwell plate. Each channel of binding beads will be mixed before
        transfer, and the samples will be mixed with the binding beads after
        the transfer. The magnetic deck activates after the addition to all
        samples, and the supernatant is removed after bead bining.
        :param vol (float): The amount of volume to aspirate from the elution
                            buffer source and dispense to each well containing
                            beads.
        :param park (boolean): Whether to save sample-corresponding tips
                               between adding elution buffer and transferring
                               supernatant to the final clean elutions PCR
                               plate.
        """
        latest_chan = -1
        for i, well in enumerate(sample_m):
            tiptrack(m1000,t1k)
            num_trans = math.ceil(vol/980)
            vol_per_trans = vol/num_trans
            source = binding_buffer
            if i == 0:
                reps = 4
            else:
                reps = 2
            mixing(source,m1000,starting_vol+binding_buffer_vol,reps=reps)
            for t in range(num_trans):
                m1000.transfer(vol_per_trans, source, well.top(), air_gap=20,
                              new_tip='never')
                m1000.air_gap(5)
            mixing(well,m1000,200,reps=4)
            m1000.blow_out(well.top(-2))
            m1000.air_gap(5)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=1800)
        ctx.delay(minutes=20,msg='Please wait 20 minutes while the sample binds with the beads.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        # grip.move(deepwell_type,h_s,magnet)
        ctx.move_labware(
            labware=sample_deepwell_plate,  # plate that is on h/s
            new_location=MAG_PLATE_SLOT,  # Mag plate
            use_gripper=USE_GRIPPER,
        )

        h_s.close_labware_latch()

        for bindi in np.arange(settling_time+2,0,-0.5): #Settling time delay with countdown timer
            ctx.delay(minutes=0.5, msg='There are ' + str(bindi) + ' minutes left in the incubation.')

        # remove initial supernatant
        remove_supernatant(vol+starting_vol)

    def wash(vol, source):

        global whichwash #Defines which wash the protocol is on to log on the app

        if source == wash1:
            whichwash = 1
        if source == wash2:
            whichwash = 2
        if source == wash3:
            whichwash = 3
        if source == wash4:
            whichwash = 4
        if source == wash5:
            whichwash = 5
        if source == wash6:
            whichwash = 6

        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(sample_m):
            tiptrack(m1000,t1k)
            src = source[i//len(source)]
            for n in range(num_trans):
                # if m1000.current_volume > 0:
                #     m1000.dispense(m1000.current_volume, waste)
                m1000.blow_out(waste)           # TODO: remove this
                m1000.transfer(vol_per_trans, src, m.top(), air_gap=20,new_tip='never')
            mixing(m, m1000, vol, reps=4)
            m1000.blow_out(m.top())
            m1000.air_gap(10)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(2000)
        ctx.delay(minutes=2,msg='Please allow 2 minutes for wash to mix on heater-shaker.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        # grip.move(deepwell_type,h_s,magnet)
        ctx.move_labware(
            labware=sample_deepwell_plate,  # plate that is on h/s
            new_location=MAG_PLATE_SLOT,  # Mag plate
            use_gripper=USE_GRIPPER,
        )
        h_s.close_labware_latch()

        for washi in np.arange(settling_time,0,-0.5): #settling time timer for washes
            ctx.delay(minutes=0.5, msg='There are ' + str(washi) + ' minutes left in wash ' + str(whichwash) + ' incubation.')

        remove_supernatant(vol)

    def dnase(vol, source):

        num_trans = math.ceil(vol/200)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(sample_m):
            tiptrack(m200, t200)
            src = source
            for n in range(num_trans):
                # if m200.current_volume > 0:
                #     m200.dispense(m200.current_volume, src.top())
                m1000.blow_out(src.top())           # TODO: remove this
                m200.transfer(vol_per_trans, src, m.top(), air_gap=20,new_tip='never')
                m200.air_gap(10)
            mixing(m, m200, vol, reps=5)
            m200.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=2000)
        h_s.set_and_wait_for_temperature(65)
        #minutes should equal 10 minus time it takes to reach 65
        ctx.delay(minutes=9,msg='Please wait 10 minutes while the dnase incubates.')
        h_s.deactivate_shaker()    
        h_s.deactivate_heater()    

    def stop_reaction(vol, source):

        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(sample_m):
            tiptrack(m1000, t1k)
            src = source[i//len(source)]
            for n in range(num_trans):
                # if m1000.current_volume > 0:
                #     m1000.dispense(m1000.current_volume, src.top())
                m1000.blow_out(src.top())           # TODO: remove this
                m1000.transfer(vol_per_trans, src, m.top(), air_gap=20,
                              new_tip='never')
                if n < num_trans - 1:  # only air_gap if going back to source
                    m1000.air_gap(20)
            mixing(m, m1000, vol+dnase_vol, reps=7)
            m1000.blow_out(m.top())
            m1000.air_gap(20)
            m1000.drop_tip()
            

        h_s.set_and_wait_for_shake_speed(rpm=1800)
        ctx.delay(minutes=10,msg='Please wait 10 minutes while the stop solution inactivates the dnase.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        # grip.move(deepwell_type,h_s,magnet)
        ctx.move_labware(
            labware=sample_deepwell_plate,  # plate that is on h/s
            new_location=MAG_PLATE_SLOT,  # Mag plate
            use_gripper=USE_GRIPPER,
        )
        h_s.close_labware_latch()

        for stop in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5,msg='There are ' + str(stop) + ' minutes left in this incubation.')

        remove_supernatant(vol+50)

    def elute(vol):
        for i, m in enumerate(sample_m):
            tiptrack(m200,tips)
            m200.aspirate(vol, elution_solution)
            m200.move_to(m.center())
            # m200.dispense(m200.current_volume, m.bottom(0.5))
            m1000.blow_out(m.bottom(0.5))  # TODO: remove this

            mixing(m, m200, elution_vol,reps=3)
            m200.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=2000)
        h_s.set_and_wait_for_temperature(60)
        ctx.delay(minutes=5,msg='Please wait 5 minutes while the sample elutes from the beads.')
        h_s.deactivate_shaker()
        h_s.deactivate_heater()

        h_s.open_labware_latch()
        # grip.move(deepwell_type,h_s,magnet)
        ctx.move_labware(
            labware=sample_deepwell_plate,  # plate that is on h/s
            new_location=MAG_PLATE_SLOT,  # Mag plate
            use_gripper=USE_GRIPPER,
        )
        h_s.close_labware_latch()

        for elutei in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5, msg='Incubating on MagDeck for ' + str(elutei) + ' more minutes.')

        for i, (m, e) in enumerate(zip(sample_m, elution_samples_m)):
            tiptrack(m200,tips)
            m200.flow_rate.aspirate = 15
            m200.flow_rate.dispense = 15
            m200.transfer(100, m.bottom(0.15), e.bottom(5), air_gap=20, new_tip='never')
            m200.blow_out(e.top(-2))
            m200.air_gap(20)
            m200.drop_tip()

    """
    Here is where you can call the methods defined above to fit your specific
    protocol. The normal sequence is:
    """
    lysis(lysis_vol, lysis_)
    bind(binding_buffer_vol)
    wash(wash_vol, wash1)
    wash(wash_vol, wash2)
    wash(wash_vol, wash3)
    #dnase1 treatment
    dnase(dnase_vol, dnase1)
    stop_reaction(stop_vol, stopreaction)
    #Resume washes
    wash(wash_vol, wash4)
    wash(wash_vol, wash5)
    drybeads = 10 #Number of minutes you want to dry for
    for beaddry in np.arange(drybeads,0,-0.5):
        ctx.delay(minutes=0.5, msg='There are ' + str(beaddry) + ' minutes left in the drying step.')
    elute(elution_vol)
