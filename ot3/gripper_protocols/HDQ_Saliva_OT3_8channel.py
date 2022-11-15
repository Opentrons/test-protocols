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

metadata = {
    "protocolName": "OT-3 HDQ DNA Extraction: Saliva",
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>'
}

requirements = {
    "robotType": "OT-3",
    'apiLevel': '2.13'
}

"""
Here is where you can modify the magnetic module engage height:
"""
whichwash = 1
tip1k = 0
tip200 = 0
drop_count = 0
MAG_PLATE_SLOT = 6


# Start protocol
def run(ctx):
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    #Protocol Parameters
    num_samples = 8
    deepwell_type = "nest_96_wellplate_2ml_deep"
    res_type="nest_12_reservoir_15ml"
    wash1_vol= 600
    wash2_vol= 600
    wash3_vol= 600
    settling_time= 4
    AL_vol= 220
    sample_vol= 500
    starting_vol= AL_vol+sample_vol 
    binding_buffer_vol= 420
    elution_vol= 100

    #magnet = ctx.load_module('magplate', '6')
    h_s = ctx.load_module('heaterShakerModuleV1', '10')
    sample_plate = h_s.load_labware(deepwell_type)
    h_s.close_labware_latch()
    elutionplate = ctx.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt', '1')
    waste = ctx.load_labware('nest_1_reservoir_195ml', '9',
                             'Liquid Waste').wells()[0].top()
    res1 = ctx.load_labware(res_type, '3', 'reagent reservoir 1')
    num_cols = math.ceil(num_samples/8)
    
    #Load tips and combine all similar boxes
    tips1000 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '2')
    tips1001 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '4')
    tips1002 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '5')
    tips1003 = ctx.load_labware('opentrons_ot3_96_tiprack_1000ul', '7')
    tips200 = ctx.load_labware('opentrons_ot3_96_tiprack_200ul', '8')
    tips = [*tips1000.wells(), *tips1001.wells(), *tips1002.wells(), *tips1003.wells()]

    # load instruments
    m1000 = ctx.load_instrument('p1000_multi_gen3', 'left')
    m200 = ctx.load_instrument('p1000_multi_gen3', 'right')

    """
    Here is where you can define the locations of your reagents.
    """
    binding_buffer = res1.wells()[0]
    elution_solution = res1.wells()[-1]
    wash1 = res1.wells()[1:3]
    wash2 = res1.wells()[3:5]
    wash3 = res1.wells()[5:7]
    AL = res1.wells()[7]

    samples_m = sample_plate.rows()[0][:num_cols]
    elution_samples_m = elutionplate.rows()[0][:num_cols]

    m1000.flow_rate.aspirate = 50
    m1000.flow_rate.dispense = 150
    m1000.flow_rate.blow_out = 300

    m200.flow_rate.aspirate = 50
    m200.flow_rate.dispense = 150
    m200.flow_rate.blow_out = 300

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
        for i, m in enumerate(samples_m):
            tiptrack(m1000,tips)
            loc = m.bottom(0.5)
            for _ in range(num_trans):
                if m1000.current_volume > 0:
                    # void air gap if necessary
                    m1000.dispense(m1000.current_volume, m.top())
                m1000.move_to(m.center())
                m1000.transfer(vol_per_trans, loc, waste, new_tip='never',
                              air_gap=20)
                m1000.blow_out(waste)
                m1000.air_gap(20)
            m1000.drop_tip()
        m1000.flow_rate.aspirate = 150
        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,h_s,use_gipper=True)
        h_s.close_labware_latch()

    def resuspend_pellet(well, pip, mvol, reps=5):
        """
        Likely unnecessary with new magnet

        'resuspend_pellet' will forcefully dispense liquid over the pellet after
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
            tiptrack(m1000, tips)
            src = source
            tvol = vol/num_transfers
            for t in range(num_transfers):
                m1000.aspirate(tvol,src.bottom(1))
                m1000.dispense(m1000.current_volume,samples_m[i].top())
                # if t == num_transfers-1:
                #     mixing(samples_m[i],m1000,tvol,reps=5)
                #     m1000.drop_tip()
            mixing(samples_m[i], m1000, tvol, reps=5)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(1800)
        ctx.delay(minutes=9, msg='Shake at 1800 rpm for 10 minutes.')
        h_s.set_and_wait_for_temperature(55)
        h_s.deactivate_shaker()
        ctx.delay(minutes=10,msg='Incubate at 55C for 10 minutes.')
        h_s.deactivate_heater()
        
        #ctx.pause("Add 5ul RNAse per sample now. Mix and incubate at RT for 2 minutes")


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
        for i, well in enumerate(samples_m):
            wall1 = samples_m[i].top().move(types.Point(x=3,y=0,z=-1))
            wall2 = samples_m[i].top().move(types.Point(x=0,y=3,z=-1))
            wall3 = samples_m[i].top().move(types.Point(x=-3,y=0,z=-1))
            wall4 = samples_m[i].top().move(types.Point(x=0,y=-3,z=-1))
            tiptrack(m1000,tips)
            num_trans = math.ceil(vol/980)
            vol_per_trans = vol/num_trans
            source = binding_buffer
            if i == 0:
                reps=3
            else:
                reps=2
            mixing(source,m1000,1000,reps=reps)
            #Transfer beads and binding from source to H-S plate
            for t in range(num_trans):
                if m1000.current_volume > 0:
                    # void air gap if necessary
                    m1000.dispense(m1000.current_volume, source.top())
                m1000.transfer(vol_per_trans, source, well.top(), air_gap=20,new_tip='never')
                if t < num_trans - 1:
                    m1000.air_gap(20)

            mixing(well,m1000,vol,reps=25)

        h_s.set_and_wait_for_shake_speed(1800)
        ctx.delay(minutes=10, msg='Shake at 1800 rpm for 10 minutes.')
        h_s.deactivate_shaker()

        #Transfer from H-S plate to Magdeck plate
        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=True)
        h_s.close_labware_latch()

        for bindi in np.arange(settling_time+1,0,-0.5): #Settling time delay with countdown timer
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

        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(samples_m):
            tiptrack(m1000,tips)
            src = source[i//(12//len(source))]
            for n in range(num_trans):
                if m1000.current_volume > 0:
                    m1000.dispense(m1000.current_volume, src.top())
                m1000.transfer(vol_per_trans, src, m.top(), air_gap=20,new_tip='never')
                m1000.air_gap(20)
            mixing(m, m1000, 200, reps=3)
            m1000.blow_out(m.top())
            m1000.air_gap(20)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(1500)
        ctx.delay(minutes=2)
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=True)
        h_s.close_labware_latch()

        for washi in np.arange(settling_time,0,-0.5): #settling time timer for washes
            ctx.delay(minutes=0.5, msg='There are ' + str(washi) + ' minutes left in wash ' + str(whichwash) + ' incubation.')

        remove_supernatant(vol)

    def elute(vol):
        for i, m in enumerate(samples_m):
            tiptrack(m200,tips200)
            m200.aspirate(vol, elution_solution)
            m200.air_gap(20)
            m200.dispense(m200.current_volume, m.top())
            mixing(m, m1000, elution_vol,reps=3)    
            m200.drop_tip()

        h_s.set_and_wait_for_shake_speed(2000)
        ctx.delay(minutes=5,msg='Shake on H-S for 5 minutes at 2000 rpm.')
        h_s.deactivate_shaker()

        #Transfer back to magnet
        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=True)
        h_s.close_labware_latch()

        for elutei in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5, msg='Incubating on MagDeck for ' + str(elutei) + ' more minutes.')

        for i, (m, e) in enumerate(zip(samples_m, elution_samples_m)):
            tiptrack(m200,tips20)
            m200.flow_rate.dispense = 10
            m200.flow_rate.aspirate = 15
            m200.transfer(vol, m.bottom(0.15), e.bottom(5), air_gap=20, new_tip='never')
            m200.blow_out(e.top(-2))
            m200.air_gap(20)
            m200.drop_tip()

    """
    Here is where you can call the methods defined above to fit your specific
    protocol. The normal sequence is:
    """
    lysis(AL_vol,AL)
    bind(binding_buffer_vol)
    wash(wash1_vol, wash1)
    wash(wash2_vol, wash2)
    wash(wash3_vol, wash3)
    drybeads = 10 #Number of minutes you want to dry for
    for beaddry in np.arange(drybeads,0,-0.5):
        ctx.delay(minutes=0.5, msg='There are ' + str(beaddry) + ' minutes left in the drying step.')
    elute(elution_vol)
