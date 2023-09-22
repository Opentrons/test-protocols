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
    'protocolName': 'Zymo_Quick_RNA_Cells_Flex.py',
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>',
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.15",
}
whichwash = 1
tip1k = 0
tip200 = 0
drop_count = 0
USE_GRIPPER = True

# SCRIPT SETTINGS
ABR_TEST                = False
if ABR_TEST == True:
    dry_run             = True          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack
else:
    dry_run             = False          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = True 

# Start protocol
def run(ctx):
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    # Protocol Parameters
    #48 Sample max
    num_samples = 48
    deepwell_type = "nest_96_wellplate_2ml_deep"
    adapter_type = "opentrons_96_deep_well_adapter"
    res_type = "nest_12_reservoir_15ml"
    if not dry_run:
        settling_time = 2
    else:
        settling_time = 0.25
    lysis_vol = 200
    binding_buffer_vol = 430 # Beads+Binding
    wash_vol = stop_vol = 500
    wash2_vol = 700
    dnase_vol = 50
    elution_vol = 100
    starting_vol= 600 # This is sample volume (400 in shield) + lysis volume

    h_s = ctx.load_module('heaterShakerModuleV1','1')
    h_s_adapter = h_s.load_adapter(adapter_type)
    sample_plate = h_s_adapter.load_labware(deepwell_type)
    h_s.close_labware_latch()
    tempdeck = ctx.load_module('Temperature Module Gen2','3')
    MAG_PLATE_SLOT = ctx.load_module('magneticBlockV1','4')
    if not dry_run:
        tempdeck.set_temperature(4)
    temp_adapter = tempdeck.load_adapter('opentrons_96_pcr_adapter')
    elutionplate = temp_adapter.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    waste = ctx.load_labware('nest_1_reservoir_195ml', '9','Liquid Waste').wells()[0].top()
    res1 = ctx.load_labware(res_type, '2', 'reagent reservoir 1')
    res2 = ctx.load_labware(res_type, '5', 'reagent reservoir 2')
    res3 = ctx.load_labware(res_type, '6', 'reagent reservoir 3')
    num_cols = math.ceil(num_samples/8)
    
    # Load tips and combine all similar boxes
    t1000 = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', '7')
    t1001 = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', '8')
    t1002 = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', '10')
    t1003 = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', '11')
    t1k = [*t1000.wells()[num_samples:96],*t1001.wells(),*t1002.wells(),*t1003.wells()]
    t1k_super = t1000.wells()[:num_samples]
    
    # load instruments
    m1000 = ctx.load_instrument('flex_8channel_1000', 'left')
    #s50 = ctx.load_instrument('p50_single_gen3', 'right',tip_racks=[t200])

    """
    Here is where you can define the locations of your reagents.
    """
    lysis_ = res1.wells()[0]
    binding_buffer = res1.wells()[1:3]
    elutionsolution = res1.wells()[-1]

    wash1 = res2.wells()[:3]
    wash2 = res2.wells()[3:6]
    wash3 = res2.wells()[6:9]
    stopreaction = res2.wells()[9:]
    
    wash4 = res3.wells()[:4]
    wash5 = res3.wells()[4:8]
    wash6 = res3.wells()[8:]

    elution_samples_m = elutionplate.rows()[0][:num_cols]
    dnase1 = elutionplate.rows()[0][num_cols:2*num_cols]
    samples_m = sample_plate.rows()[0][:num_cols]

    m1000.flow_rate.aspirate = 300
    m1000.flow_rate.dispense = 300
    m1000.flow_rate.blow_out = 300
    
    def tiptrack(pip, tipbox):
        global tip1k
        global tip200
        global drop_count
        if pip == m1000:
            pip.pick_up_tip(tipbox[int(tip1k)])
            tip1k = tip1k + 8
        drop_count = drop_count + 8
        if drop_count >= 150:
            drop_count = 0
            ctx.pause("Please empty the waste bin of all the tips before continuing.")

    def blink():
        for i in range(3):
            ctx.set_rail_lights(True)
            ctx.delay(minutes=0.01666667)
            ctx.set_rail_lights(False)
            ctx.delay(minutes=0.01666667)

    def remove_supernatant(vol):
        ctx.comment('-----Removing Supernatant-----')
        m1000.flow_rate.aspirate = 30
        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans

        def _waste_track(vol):
            global waste_vol 
            waste_vol = waste_vol + (vol*8)
            if waste_vol >= 185000:
                m1000.home()
                blink()
                ctx.pause('Please empty liquid waste before resuming.')
                waste_vol = 0

        for i, m in enumerate(samples_m):
            m1000.pick_up_tip(t1k_super[8*i])
            loc = m.bottom(0.5)
            for _ in range(num_trans):
                if m1000.current_volume > 0:
                    # void air gap if necessary
                    m1000.dispense(m1000.current_volume, m.top())
                m1000.move_to(m.center())
                m1000.transfer(vol_per_trans, loc, waste, new_tip='never',air_gap=20)
                m1000.blow_out(waste)
                m1000.air_gap(20)
            m1000.drop_tip(t1k_super[8*i])
        m1000.flow_rate.aspirate = 300
        #Move Plate From Magnet to H-S
        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,h_s_adapter,use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

    def bead_mixing(well, pip, mvol, reps=8):
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
        aspbot = well.bottom().move(types.Point(x=0,y=3,z=1))
        asptop = well.bottom().move(types.Point(x=0,y=-3,z=5))
        disbot = well.bottom().move(types.Point(x=0,y=2,z=3))
        distop = well.top().move(types.Point(x=0,y=1,z=0))

        if mvol > 1000:
            mvol = 1000

        vol = mvol * .9

        pip.flow_rate.aspirate = 500
        pip.flow_rate.dispense = 500

        pip.move_to(center)
        for _ in range(reps):
            pip.aspirate(vol,aspbot)
            pip.dispense(vol,distop)
            pip.aspirate(vol,asptop)
            pip.dispense(vol,disbot)
            if _ == reps-1:
                pip.flow_rate.aspirate = 150
                pip.flow_rate.dispense = 100
                pip.aspirate(vol,aspbot)
                pip.dispense(vol,aspbot)

        pip.flow_rate.aspirate = 300
        pip.flow_rate.dispense = 300

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
        center = well.top(5)
        asp = well.bottom(1)
        disp = well.top(-8)

        if mvol > 1000:
            mvol = 1000

        vol = mvol * .9

        pip.flow_rate.aspirate = 500
        pip.flow_rate.dispense = 500

        pip.move_to(center)
        for _ in range(reps):
            pip.aspirate(vol,asp)
            pip.dispense(vol,disp)
            pip.aspirate(vol,asp)
            pip.dispense(vol,disp)
            if _ == reps-1:
                pip.flow_rate.aspirate = 150
                pip.flow_rate.dispense = 100
                pip.aspirate(vol,asp)
                pip.dispense(vol,asp)

        pip.flow_rate.aspirate = 300
        pip.flow_rate.dispense = 300

    def lysis(vol, source):
        ctx.comment('-----Beginning Lysis-----')
        num_transfers = math.ceil(vol/980)
        tiptrack(m1000, t1k)
        for i in range(num_cols):
            src = source
            tvol = vol/num_transfers
            for t in range(num_transfers):
                m1000.aspirate(tvol,src.bottom(1))
                m1000.dispense(m1000.current_volume,samples_m[i].top(-3))

        for i in range(num_cols):
            if i != 0:
                tiptrack(m1000,t1k)
            mixing(samples_m[i],m1000,starting_vol,reps=8 if not dry_run else 1)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=2000)
        ctx.delay(minutes=2 if not dry_run else 0.1,msg='Please wait 2 minutes while the lysis buffer mixes with the sample.')
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
        ctx.comment('-----Beginning Bind Steps-----')
        for i, well in enumerate(samples_m):
            tiptrack(m1000,t1k)
            num_trans = math.ceil(vol/980)
            vol_per_trans = vol/num_trans
            source = binding_buffer[i//3]
            if i == 0 or i == 3:
                r = 6
            else:
                r = 1
            mixing(source,m1000,binding_buffer_vol,reps=r if not dry_run else 1)
            for t in range(num_trans):
                m1000.transfer(vol_per_trans, source.bottom(1), well.top(), air_gap=20, new_tip='never')
                m1000.air_gap(5)
            mixing(well,m1000,vol+starting_vol,reps=4 if not dry_run else 1)
            m1000.blow_out(well.top(-2))
            m1000.air_gap(5)
            m1000.drop_tip()

        ctx.comment('-----Incubating Bind on Heater-Shaker-----')
        h_s.set_and_wait_for_shake_speed(rpm=1650)
        ctx.delay(minutes=20 if not dry_run else 0.1,msg='Please wait 20 minutes while the sample binds with the beads.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for bindi in np.arange(settling_time+1,0,-0.5): # Settling time delay with countdown timer
            ctx.delay(minutes=0.5, msg='There are ' + str(bindi) + ' minutes left in the incubation.')

        # remove initial supernatant
        remove_supernatant(vol+starting_vol)

    def wash(vol, source):

        global whichwash # Defines which wash the protocol is on to log on the app

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

        if vol == wash_vol:
                speed = 2000
        if vol == wash2_vol:
                speed = 1850

        ctx.comment('-----Beginning Wash #' + str(whichwash) + '-----')
        
        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans
        tiptrack(m1000,t1k)
        for i, m in enumerate(samples_m):
            if vol == wash_vol:
                src = source[i//2] #3 wells each
            if vol == wash2_vol:
                if i <=3:
                    src = source[i] #4 wells each
                if i == 4:
                    m1000.aspirate(vol_per_trans/2,source[0])
                    m1000.dispense(vol_per_trans/2,source[1])
                    src = source[1]
                if i == 5:
                    m1000.aspirate(vol_per_trans/2,source[2])
                    m1000.dispense(vol_per_trans/2,source[3])
                    src = source[3]
            for n in range(num_trans):
                m1000.transfer(vol_per_trans, src.bottom(1), m.top(), air_gap=20,new_tip='never')
            m1000.blow_out(m.top())
            m1000.air_gap(10)
        m1000.drop_tip()    

        h_s.set_and_wait_for_shake_speed(speed)
        ctx.delay(minutes=5 if not dry_run else 0.1,msg='Please allow 5 minutes for wash to mix on heater-shaker.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for washi in np.arange(settling_time,0,-0.5): # settling time timer for washes
            ctx.delay(minutes=0.5, msg='There are ' + str(washi) + ' minutes left in wash ' + str(whichwash) + ' incubation.')

        remove_supernatant(vol)

    def dnase(vol, source):
        ctx.comment('-----Beginning DNAseI Steps-----')
        num_trans = math.ceil(vol/200)
        vol_per_trans = vol/num_trans
        tiptrack(m1000, t1k)

        for i, m in enumerate(samples_m):
            src = source
            for n in range(num_trans):
                m1000.flow_rate.aspirate = 15
                m1000.aspirate(vol,src[i])
                m1000.dispense(vol,m.top(-5))
                m1000.blow_out()

        m1000.flow_rate.aspirate = 300

        for i in range(num_cols):
            if i != 0:
                tiptrack(m1000,t1k)
            mixing(samples_m[i], m1000, vol, reps=8 if not dry_run else 1)
            m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=2000)
        if not dry_run:
            h_s.set_and_wait_for_temperature(65)
        # minutes should equal 10 minus time it takes to reach 65
        ctx.delay(minutes=5 if not dry_run else 0.1,msg='Please wait 10 minutes while the dnase incubates.')
        h_s.deactivate_shaker()    

    def stop_reaction(vol, source):
        ctx.comment('-----Adding Stop Solution to Inactivate DNAseI-----')
        num_trans = math.ceil(vol/980)
        vol_per_trans = vol/num_trans
        tiptrack(m1000, t1k)
        for i, m in enumerate(samples_m):
            src = source[i//2]
            for n in range(num_trans):
                if m1000.current_volume > 0:
                    m1000.dispense(m1000.current_volume, src.top())
                m1000.transfer(vol_per_trans, src.bottom(1), m.top(), air_gap=20, new_tip='never')
            
        m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=1500)
        ctx.delay(minutes=10 if not dry_run else 0.1,msg='Please wait 10 minutes while the stop solution inactivates the dnase.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for stop in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5,msg='There are ' + str(stop) + ' minutes left in this incubation.')

        remove_supernatant(vol+50)

    def elute(vol):
        ctx.comment('-----Beginning Elution Steps-----')
        tiptrack(m1000, t1k)
        for i, m in enumerate(samples_m):
            m1000.aspirate(vol, elutionsolution.bottom(1))
            m1000.dispense(m1000.current_volume, m.top(-2))
            m1000.blow_out(m.top(-2))
        
        m1000.drop_tip()

        h_s.set_and_wait_for_shake_speed(rpm=2000)
        ctx.delay(minutes=5 if not dry_run else 0.1,msg='Please wait 5 minutes while the sample elutes from the beads.')
        h_s.deactivate_shaker()

        h_s.open_labware_latch()
        ctx.move_labware(sample_plate,MAG_PLATE_SLOT,use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for elutei in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5, msg='Incubating on MagDeck for ' + str(elutei) + ' more minutes.')

        for i, (m, e) in enumerate(zip(samples_m, elution_samples_m)):
            tiptrack(m1000, t1k)
            m1000.flow_rate.aspirate = 75
            m1000.flow_rate.dispense = 150
            m1000.transfer(100, m.bottom(0.15), e.bottom(5), air_gap=20, new_tip='never')
            m1000.blow_out(e.top(-2))
            m1000.air_gap(10)
            m1000.drop_tip()

    """
    Here is where you can call the methods defined above to fit your specific
    protocol. The normal sequence is:
    """
    lysis(lysis_vol, lysis_)
    bind(binding_buffer_vol)
    wash(wash_vol, wash1)
    if not dry_run:
        wash(wash_vol, wash2)
        wash(wash_vol, wash3)
    # dnase1 treatment
    dnase(dnase_vol, dnase1)
    stop_reaction(stop_vol, stopreaction)
    
    if not dry_run:
        # Resume washes
        wash(wash2_vol, wash4)
        wash(wash2_vol, wash5)
        wash(wash2_vol, wash6)
        drybeads = 10 # Number of minutes you want to dry for
    else:
        drybeads = 0.5
    for beaddry in np.arange(drybeads,0,-0.5):
        ctx.delay(minutes=0.5, msg='There are ' + str(beaddry) + ' minutes left in the drying step.')
    elute(elution_vol)