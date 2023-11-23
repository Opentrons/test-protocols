from opentrons.types import Point
import json
import os
import math
from time import sleep
from opentrons import types
import numpy as np

metadata = {
    'protocolName': 'Flex Macherey-Nagel Nucleomag DNA Extraction: Tissue, Cells, Bacteria 96 channel',
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>'
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

dry_run = False
M_N_DW = True
HS_SLOT = 1
USE_GRIPPER = True

ABR_TEST                = True
if ABR_TEST == True:
    DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack
else:
    DRYRUN              = False          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = True 


# Start protocol
def run(ctx):
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    if M_N_DW:
        deepwell_type = "macherey_nagel_dwplate_2200ul"
    else:
        deepwell_type = "nest_96_wellplate_2ml_deep"
    res_type = "nest_96_wellplate_2ml_deep"
    wash1_vol = wash2_vol = 600
    wash3_vol = 900
    if not dry_run:
        settling_time = 3.5
        lysis_incubation = 80
    if dry_run:
        settling_time= 0.25
        lysis_incubation = 0.25

    h_s = ctx.load_module('heaterShakerModuleV1', HS_SLOT)
    if M_N_DW:
        h_s_adapter = h_s.load_adapter('opentrons_universal_flat_adapter')
    else:
        h_s_adapter = h_s.load_adapter('opentrons_96_deep_well_adapter')
    sample_plate = h_s_adapter.load_labware(deepwell_type,'Sample Plate')
    samples_m = sample_plate.wells()[0]
    
    temp = ctx.load_module('temperature module gen2','D3')
    tempblock = temp.load_adapter('opentrons_96_well_aluminum_block')
    magblock = ctx.load_module('magneticBlockV1','C1')
    elutionplate = tempblock.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt','Elution Plate/ Reservoir')
    waste_ = ctx.load_labware('nest_1_reservoir_195ml', 'B3','Liquid Waste').wells()[0].top()

    lysis_res = ctx.load_labware(res_type, 'D2','Lysis reservoir').wells()[0] 
    bind_res = ctx.load_labware(res_type, 'C2','Beads and binding reservoir').wells()[0] 
    wash1_res = ctx.load_labware(res_type, 'C3','Wash 1 reservoir').wells()[0]
    wash2_res = ctx.load_labware(res_type, 'B1','Wash 2 reservoir').wells()[0]
    wash3_res = ctx.load_labware(res_type, 'B2','Wash 3 reservoir').wells()[0]
    elution_res = elutionplate.wells()[0]

    #Load tips
    tips = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'A1',adapter='opentrons_flex_96_tiprack_adapter').wells()[0]
    tips1 = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'A2',adapter='opentrons_flex_96_tiprack_adapter').wells()[0]

    #Differences between sample types
    lysis_vol = 225
    sample_vol = 10
    starting_vol = lysis_vol+sample_vol 
    binding_buffer_vol = 385
    elution_vol = 100

    # load 96 channel pipette
    pip = ctx.load_instrument('flex_96channel_1000', mount="left")

    pip.flow_rate.aspirate = 100
    pip.flow_rate.dispense = 150
    pip.flow_rate.blow_out = 300

    def resuspend_pellet(vol,plate,reps=3):
        pip.flow_rate.aspirate = 150
        pip.flow_rate.dispense = 200

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
            if _ == reps-1:
                pip.flow_rate.aspirate = 50
                pip.flow_rate.dispense = 30
                pip.aspirate(mixvol,loc8)
                pip.dispense(mixvol,loc8)

        pip.flow_rate.aspirate = 50
        pip.flow_rate.dispense = 150


    def bead_mix(vol,plate,reps=5):
        pip.flow_rate.aspirate = 150
        pip.flow_rate.dispense = 200

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
            if _ == reps-1:
                pip.flow_rate.aspirate = 50
                pip.flow_rate.dispense = 30
                pip.aspirate(mixvol,loc1)
                pip.dispense(mixvol,loc1)

        pip.flow_rate.aspirate = 50
        pip.flow_rate.dispense = 150

    #Just in case
    h_s.close_labware_latch()

    #Start Protocol

    #Transfer and mix lysis
    ctx.comment("-------Lysis is starting now-------")
    pip.pick_up_tip(tips)
    for x in range(4 if not dry_run else 1): #Mix PK and Lysis
        pip.aspirate(lysis_vol,lysis_res)
        pip.dispense(lysis_vol,lysis_res.top(-5))    
    pip.aspirate(lysis_vol,lysis_res)
    pip.dispense(lysis_vol,samples_m)
    resuspend_pellet(lysis_vol,samples_m,reps=5 if not dry_run else 1)
    pip.return_tip()
    
    #Mix, then heat
    h_s.set_and_wait_for_shake_speed(1500)
    ctx.delay(minutes=lysis_incubation,msg='Please wait 80 minutes to allow for proper lysis mixing.')
    h_s.deactivate_shaker()

    #Transfer and mix bind&beads
    ctx.comment("-------Bind steps are starting now-------")
    pip.pick_up_tip(tips)
    bead_mix(binding_buffer_vol,bind_res, reps=5 if not dry_run else 1)
    pip.aspirate(binding_buffer_vol,bind_res)
    pip.dispense(binding_buffer_vol,samples_m)
    if binding_buffer_vol+starting_vol < 1000:
        mix_vol = binding_buffer_vol+starting_vol
    else:
        mix_vol = 1000
    bead_mix(mix_vol,samples_m,reps=7 if not dry_run else 1)
    pip.return_tip()

    #Shake for binding incubation
    h_s.set_and_wait_for_shake_speed(rpm=1800)
    ctx.delay(minutes=5 if not dry_run else 0.25,msg='Please allow 5 minutes for the beads to bind the DNA.')
    h_s.deactivate_shaker()

    h_s.open_labware_latch()
    #Transfer plate to magnet
    ctx.move_labware(
        sample_plate, 
        magblock, 
        use_gripper=USE_GRIPPER
    )
    h_s.close_labware_latch()

    ctx.delay(minutes=settling_time,msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

    #Remove Supernatant and move off magnet
    ctx.comment("-------Removing Supernatant-------")
    pip.pick_up_tip(tips)
    pip.flow_rate.aspirate = 35
    pip.aspirate(1000,samples_m.bottom(0.3))
    pip.dispense(1000,waste_)
    if starting_vol+binding_buffer_vol > 1000:
        rest = (starting_vol+binding_buffer_vol)-900
        pip.aspirate(rest,samples_m.bottom(0.2)) #original = .1
        pip.dispense(rest,waste_)
    pip.return_tip()
    pip.flow_rate.aspirate = 100

    #Transfer plate from magnet to H/S
    h_s.open_labware_latch()
    ctx.move_labware(
        sample_plate, 
        h_s_adapter, 
        use_gripper=USE_GRIPPER
    )
    
    h_s.close_labware_latch()

    #Washes
    for i in range(2 if not dry_run else 1):
        if i == 0:
            wash_res = wash1_res
            wash_vol = wash1_vol
            w=1
        else:
            wash_res = wash2_res
            wash_vol = wash2_vol
            w=2
        ctx.comment("-------Wash "+str(w)+" is starting now-------")

        #Quick H-S shake to loosen pellet
        h_s.set_and_wait_for_shake_speed(1800)
        ctx.delay(seconds = 20,msg='Please wait 20 seconds to loosen pellet before dispensing wash')
        h_s.deactivate_shaker()

        pip.pick_up_tip(tips)
        pip.aspirate(wash_vol,wash_res)
        pip.dispense(wash_vol,samples_m)
        pip.return_tip()
        pip.home()

        h_s.set_and_wait_for_shake_speed(rpm=1800)
        ctx.delay(minutes=5 if not dry_run else 0.25,msg='5 minutes in Wash '+str(w)+' incubation.')
        h_s.deactivate_shaker()
        h_s.open_labware_latch()

        #Transfer plate to magnet
        ctx.move_labware(
            sample_plate, 
            magblock, 
            use_gripper=USE_GRIPPER
        )

        ctx.delay(minutes=settling_time,msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet in Wash '+str(w))

        #Remove Supernatant and move off magnet
        ctx.comment("-------Removing Supernatant-------")
        pip.pick_up_tip(tips)
        pip.flow_rate.aspirate = 35
        pip.aspirate(wash_vol+50,samples_m.bottom(0.3))
        pip.dispense(wash_vol+50,waste_)
        pip.flow_rate.aspirate = 100
        if i == 0:
            pip.return_tip()
            #Transfer plate from magnet to H/S
            ctx.move_labware(
                sample_plate, 
                h_s_adapter, 
                use_gripper=USE_GRIPPER
            )
            h_s.close_labware_latch()

    if not dry_run:
        #Wash3
        ctx.comment("-------Wash 3 is starting now-------")
        pip.aspirate(wash3_vol,wash3_res)
        pip.flow_rate.dispense = 30
        pip.dispense(wash3_vol,samples_m)
        pip.air_gap(10)
        ctx.delay(seconds=20,msg='Please allow 45 seconds for wash buffer to settle and clear well.')

        pip.flow_rate.dispense = 150

        #Clear Wash 3 from samples
        pip.aspirate(wash3_vol,samples_m.bottom(.2)) 
        pip.dispense(wash3_vol,wash3_res)
        pip.blow_out(wash3_res)
        pip.air_gap(10)
        pip.return_tip()

    #Transfer plate from magnet to H/S
    ctx.move_labware(
        sample_plate, 
        h_s_adapter, 
        use_gripper=USE_GRIPPER
    )
    h_s.close_labware_latch()

    pip.flow_rate.aspirate = 35

    #Elution
    pip.pick_up_tip(tips1)
    pip.aspirate(elution_vol, elution_res)
    pip.dispense(elution_vol, samples_m)
    pip.return_tip()

    h_s.set_and_wait_for_shake_speed(rpm=2000)
    ctx.delay(minutes=5 if not dry_run else 0.25, msg='Please wait 5 minutes to allow dna to elute from beads.')
    h_s.deactivate_shaker()
    h_s.open_labware_latch()

    #Transfer plate to magnet
    ctx.move_labware(
        sample_plate, 
        magblock, 
        use_gripper=USE_GRIPPER
    )

    ctx.delay(minutes=settling_time,msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

    pip.pick_up_tip(tips1)
    pip.aspirate(elution_vol,samples_m.bottom(0.2)) #original = .15
    pip.dispense(elution_vol,elutionplate.wells()[0])
    pip.return_tip()

    pip.home()