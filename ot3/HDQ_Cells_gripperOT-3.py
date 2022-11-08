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
    'protocolName': 'Omega HDQ DNA Extraction with Lysis: Cells (with gripper)',
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>',
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.13",
}

"""
Here is where you can modify the magnetic module engage height:
"""

# Start protocol
def run(ctx):
    #Set Email Parameters
    #Create your SMTP session 
    smtp = smtplib.SMTP('smtp.gmail.com', 587) 

    #Use TLS to add security 
    smtp.starttls() 

    sender_email = "opentrons.alert@gmail.com"
    receiver_email = "6318169036@tmomail.net"
    password = "yzipggnhgxjlpuck" #App(python)-specific password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Alert"
    body = "Please change the tips.\n"

    msg.attach(MIMEText(body,'plain'))

    sms = msg.as_string()

    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    #Same for all HDQ Extractions
    num_samples = 96
    #Determines how many pipets to use- any # or divisible by 8?
    num_pips = math.ceil(num_samples/8)*8
    
    deepwell_type = "nest_96_wellplate_2ml_deep"
    res_type="nest_12_reservoir_15ml"
    wash_vol= 600
    num_washes = 3
    settling_time= 4

    h_s = ctx.load_module('heaterShakerModuleV1','10')
    sample_plate = h_s.load_labware(deepwell_type)
    # magnet = ctx.load_module('ring_magnet', '6')      # No need to load magnetic module. Mag plate requires no loading
    elutionplate = ctx.load_labware('opentrons_96_aluminumblock_nest_wellplate_100ul','1')

    #Cut waste out?
    waste = ctx.load_labware('nest_1_reservoir_195ml', '9',
                             'Liquid Waste').wells()[0].top()
    #??

    lysis_res = ctx.load_labware(deepwell_type, '5')
    elution_res = ctx.load_labware(deepwell_type, '4')
    wash_res = ctx.load_labware(deepwell_type, '7')
    bind_res = ctx.load_labware(deepwell_type, '8')
    
    #Load tips and combine all similar boxes
    tips = ctx.load_labware('opentrons_96_filtertiprack_1000ul', '2')
    tips1 = ctx.load_labware('opentrons_96_filtertiprack_1000ul', '3')

    #Differences between sample types
    AL_vol= 250
    sample_vol= 180
    inc_temp= 55
    starting_vol= AL_vol+sample_vol 
    binding_buffer_vol= 340
    elution_vol= 50

    # load 96 channel pipette
    pip = ctx.load_instrument('96_channel')

    pip.flow_rate.aspirate = 50
    pip.flow_rate.dispense = 150
    pip.flow_rate.blow_out = 300

    #start protocol
    def resuspend_pellet(vol,plate,reps=3):
        loc1 = plate.bottom().move(types.Point(x=1,y=0,z=1))
        loc2 = plate.bottom().move(types.Point(x=0.75,y=0.75,z=1))
        loc3 = plate.bottom().move(types.Point(x=0,y=1,z=1))
        loc4 = plate.bottom().move(types.Point(x=-0.75,y=0.75,z=1))
        loc5 = plate.bottom().move(types.Point(x=-1,y=0,z=1))
        loc6 = plate.bottom().move(types.Point(x=-0.75,y=0-0.75,z=1))
        loc7 = plate.bottom().move(types.Point(x=0,y=-1,z=1))
        loc8 = plate.bottom().move(types.Point(x=0.75,y=-0.75,z=1))

        if vol>1000:
            vol = 1000

        mixvol = vol*.9

        for _ in range(reps):
            pip.aspirate(mixvol,loc1)
            pip.dispense(mixvol,loc1)
            pip.aspirate(mixvol,loc2)
            pip.dispense(mixvol,loc2)
            pip.aspirate(mixvol,loc3)
            pip.dispense(mixvol,loc3)
            pip.aspirate(mixvol,loc4)
            pip.dispense(mixvol,loc4)
            pip.aspirate(mixvol,loc5)
            pip.dispense(mixvol,loc5)
            pip.aspirate(mixvol,loc6)
            pip.dispense(mixvol,loc6)
            pip.aspirate(mixvol,loc7)
            pip.dispense(mixvol,loc7)
            pip.aspirate(mixvol,loc8)
            pip.dispense(mixvol,loc8)

    def bead_mix(vol,plate,reps=5):
        loc1 = plate.bottom().move(types.Point(x=0,y=0,z=1))
        loc2 = plate.bottom().move(types.Point(x=0,y=0,z=8))
        loc3 = plate.bottom().move(types.Point(x=0,y=0,z=16))
        loc4 = plate.bottom().move(types.Point(x=0,y=0,z=24))

        if vol>1000:
            vol = 1000

        mixvol = vol*.9

        for _ in range(reps):
            pip.aspirate(mixvol,loc1)
            pip.dispense(mixvol,loc1)
            pip.aspirate(mixvol,loc1)
            pip.dispense(mixvol,loc2)
            pip.aspirate(mixvol,loc1)
            pip.dispense(mixvol,loc3)
            pip.aspirate(mixvol,loc1)
            pip.dispense(mixvol,loc4)

    #Just in case
    h_s.close_latch()

    #Transfer and mix lysis
    pip.pick_up_tip(tips)
    pip.aspirate(AL_vol,lysis_res)
    pip.dispense(AL_vol,sample_plate)
    pip.resuspend_pellet(starting_vol,sample_plate,reps=4)
    pip.drop_tip(tips)
    
    #Mix, then heat
    h_s.set_and_wait_for_shake_speed(rpm=1800)
    ctx.delay(minutes=10)

    h_s.deactivate_shaker()
    h_s.set_and_wait_for_temperature(celcius=55)
    ctx.delay(minutes=10)

    h_s.deactive_heater()



    #Transfer and mix bind&beads
    pip.pick_up_tip(tips1)
    pip.bead_mix(binding_buffer_vol,bind_res)
    pip.aspirate(binding_buffer_vol,bind_res)
    pip.dispense(binding_buffer_vol,sample_plate)
    pip.bead_mix(binding_buffer_vol+starting_vol,sample_plate,reps=7)
    pip.home()

    #Shake for binding incubation
    h_s.set_and_wait_for_shake_speed(rpm=1800)
    ctx.delay(minutes=10)

    h_s.deactivate_shaker()
    h_s.open_latch()

    #Transfer plate to magnet
    # grip.move(deepwell_type,h_s,magnet)
    ctx.move_labware(
        labware=sample_plate,  # plate that is on h/s
        new_location=6,         # Mag plate
        use_gripper=True,
    )
    ctx.delay(minutes=settling_time,msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')



    #Remove Supernatant and move off magnet
    pip.aspirate(1000,sample_plate.bottom(0.3))
    pip.dispense(1000,waste)
    if starting_vol+binding_buffer_vol > 1000:
        pip.aspirate(1000,sample_plate.bottom(0.3))
        pip.dispense(1000,waste)

    # grip.move(deepwell_type,magnet,h_s)
    ctx.move_labware(
        labware=sample_plate,  # plate that is on mag plate
        new_location=h_s,
        use_gripper=True,
    )
    h_s.close_latch()



    #Washes
    for i in range(num_washes)
        pip.aspirate(wash_vol,wash_res)
        pip.dispense(wash_vol,sample_plate)
        pip.resuspend_pellet(wash1_vol,sample_plate)

        pip.home()

        h_s.set_and_wait_for_shake_speed(rpm=1800)
        ctx.delay(minutes=2)
        h_s.deactivate_shaker()
        h_s.open_latch()

        #Transfer plate to magnet
        # grip.move(deepwell_type,h_s,magnet)
        ctx.move_labware(
            labware=sample_plate,  # plate that is on h/s
            new_location=6,  # Mag plate
            use_gripper=True,
        )
        ctx.delay(minutes=settling_time,msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

        #Remove Supernatant and move off magnet
        pip.aspirate(1000,sample_plate.bottom(0.3))
        pip.dispense(1000,bind_res.top())
        if wash_vol > 1000:
            pip.aspirate(1000,sample_plate.bottom(0.3))
            pip.dispense(1000,bind_res.top())

        # grip.move(deepwell_type,magnet,h_s)
        ctx.move_labware(
            labware=sample_plate,  # plate that is on mag plate
            new_location=h_s,
            use_gripper=True,
        )
        h_s.close_latch()



    #Dry beads
    drybeads = 10 #Number of minutes you want to dry for
    for beaddry in np.arange(drybeads,0,-0.5):
        ctx.delay(minutes=0.5, msg='There are ' + str(beaddry) + ' minutes left in the drying step.')



    #Elution
    pip.aspirate(elution_vol, elution_res)
    pip.dispense(elution_vol, sample_plate)
    pip.resuspend_pellet(elution_vol,sample_plate)
    pip.home()

    h_s.set_and_wait_for_shake_speed(rpm=2000)
    ctx.delay(minutes=5, msg='Please wait 5 minutes to allow dna to elute from beads.')
    h_s.deactivate_shaker()
    h_s.open_latch()

    # grip.move(deepwell_type,h_s,magnet)
    ctx.move_labware(
        labware=sample_plate,  # plate that is on h/s
        new_location=6,  # Mag plate
        use_gripper=True,
    )

    ctx.delay(minutes=settling_time,msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

    pip.aspirate(elution_vol,sample_plate)
    pip.dispense(elution_vol,elutionplate)
    pip.drop_tip(tips1)

    pip.home()
