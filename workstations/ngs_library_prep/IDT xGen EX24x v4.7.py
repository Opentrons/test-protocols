from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'IDT xGen EZ 24x v4.7',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

# SCRIPT SETTINGS
DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
USE_GRIPPER         = True          # True = Uses Gripper, False = Manual Move
TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack

# PROTOCOL SETTINGS
COLUMNS             = 3             # 1 - 3
FRAGTIME            = 38            # Minutes, Duration of the Fragmentation Step
PCRCYCLES           = 7             # Amount of PCR cycles

# PROTOCOL BLOCKS                   # Skip steps or do off deck thermocycling
STEP_FRERAT         = 1
STEP_FRERATDECK     = 1
STEP_LIG            = 1
STEP_LIGDECK        = 1
STEP_POSTLIG        = 1
STEP_PCR            = 1
STEP_PCRDECK        = 1
STEP_POSTPCR        = 1

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

p200_tips = 0
p50_tips  = 0

ABR_TEST            = True
if ABR_TEST == True:
    DRYRUN          = True           # Overrides to only DRYRUN
    TIP_TRASH       = False          # Overrides to only REUSING TIPS
    RUN             = 1             # Repetitions
else:
    RUN             = 1

def run(protocol: protocol_api.ProtocolContext):

    global p200_tips
    global p50_tips

    if ABR_TEST == True:
        protocol.comment('THIS IS A ABR RUN WITH '+str(RUN)+' REPEATS') 
    protocol.comment('THIS IS A DRY RUN') if DRYRUN == True else protocol.comment('THIS IS A REACTION RUN')
    protocol.comment('USED TIPS WILL GO IN TRASH') if TIP_TRASH == True else protocol.comment('USED TIPS WILL BE RE-RACKED')

    # DECK SETUP AND LABWARE
    # ========== FIRST ROW ===========
    heatershaker        = protocol.load_module('heaterShakerModuleV1','D1')
    hs_adapter          = heatershaker.load_adapter('opentrons_96_pcr_adapter')    
    if RES_TYPE == '12x15ml':
        reservoir       = protocol.load_labware('nest_12_reservoir_15ml','D2')
    if RES_TYPE == '96x2ml':
        reservoir       = protocol.load_labware('nest_96_wellplate_2ml_deep','D2')   
    temp_block          = protocol.load_module('temperature module gen2', 'D3')
    temp_adapter        = temp_block.load_adapter('opentrons_96_well_aluminum_block')
    reagent_plate       = temp_adapter.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    # ========== SECOND ROW ==========
    mag_block           = protocol.load_module('magneticBlockV1', 'C1')
    tiprack_200_1       = protocol.load_labware('opentrons_flex_96_tiprack_200ul',  'C2')
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_50ul',  'C3')
    # ========== THIRD ROW ===========
    thermocycler        = protocol.load_module('thermocycler module gen2')
    sample_plate_1      = thermocycler.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    tiprack_200_2       = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'B2')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_50ul','B3')
    # ========== FOURTH ROW ==========
    tiprack_200_3       = protocol.load_labware('opentrons_flex_96_tiprack_200ul',  'A2')

    # ========= REAGENT PLATE ======== 
    FRERAT              = reagent_plate.wells_by_name()['A1']
    LIG                 = reagent_plate.wells_by_name()['A2']
    PCR                 = reagent_plate.wells_by_name()['A3']
    RSB                 = reagent_plate.wells_by_name()['A4']
    Barcodes_1          = reagent_plate.wells_by_name()['A7']
    Barcodes_2          = reagent_plate.wells_by_name()['A8']
    Barcodes_3          = reagent_plate.wells_by_name()['A9']

    # =========== RESERVOIR ==========
    AMPure              = reservoir['A1']    
    EtOH_1              = reservoir['A3']
    EtOH_2              = reservoir['A4']
    EtOH_3              = reservoir['A5']
    Liquid_trash_well_1 = reservoir['A10']
    Liquid_trash_well_2 = reservoir['A11']
    Liquid_trash_well_3 = reservoir['A12']

    # pipette
    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_200_1,tiprack_200_2,tiprack_200_3])
    p50 = protocol.load_instrument("flex_8channel_50", "right", tip_racks=[tiprack_50_1,tiprack_50_2])
    
    #tip and sample tracking
    if COLUMNS == 1:
        column_1_list = ['A1']
        column_2_list = ['A4']
        column_3_list = ['A7']
        column_4_list = ['A10']
        barcodes = ['A7']
    if COLUMNS == 2:
        column_1_list = ['A1','A2']
        column_2_list = ['A4','A5']
        column_3_list = ['A7','A8']
        column_4_list = ['A10','A11']
        barcodes = ['A7','A8']
    if COLUMNS == 3:
        column_1_list = ['A1','A2','A3']
        column_2_list = ['A4','A5','A6']
        column_3_list = ['A7','A8','A9']
        column_4_list = ['A10','A11','A12']
        barcodes = ['A7','A8','A9']

    def tipcheck():
        if p200_tips >= 3*12:
            if ABR_TEST == True: 
                p1000.reset_tipracks()
            else:
                protocol.pause('RESET p200 TIPS')
                p1000.reset_tipracks()
            p200_tips == 0 
        if p50_tips >= 2*12:
            if ABR_TEST == True: 
                p50.reset_tipracks()
            else:
                protocol.pause('RESET p50 TIPS')
                p50.reset_tipracks()
            p50_tips == 0

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################
    # commands
    for loop in range(RUN):
        thermocycler.open_lid()
        heatershaker.open_labware_latch()
        if DRYRUN == False:
            protocol.comment("SETTING THERMO and TEMP BLOCK Temperature")
            thermocycler.set_block_temperature(4)
            thermocycler.set_lid_temperature(70)    
            temp_block.set_temperature(4)
        protocol.pause("Ready")
        heatershaker.close_labware_latch()
        Liquid_trash = Liquid_trash_well_1

        # Sample Plate contains 100ng of DNA in 19.5ul Low EDTA TE

        if STEP_FRERAT == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Fragmenting / End Repair / A-Tailing')
            protocol.comment('==============================================')
            #Standard Setup

            protocol.comment('--> Adding FRERAT')
            FRERATVol    = 10.5
            FRERATMixRep = 25 if DRYRUN == False else 1
            FRERATMixVol = 25
            for loop, X in enumerate(column_1_list):
                p50.pick_up_tip()
                p50.aspirate(FRERATVol, FRERAT.bottom(z=0.3)) #original = .3
                p50.dispense(FRERATVol, sample_plate_1[X].bottom(z=0.3)) #original = .3
                p50.move_to(sample_plate_1[X].bottom(z=0.5)) #original = .5
                p50.mix(FRERATMixRep,FRERATMixVol)
                p50.blow_out(sample_plate_1[X].top(z=-1))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()

        if STEP_FRERATDECK == 1:
            ############################################################################################################################################
            protocol.comment('Seal, Run FRERAT (~70min)')
            thermocycler.close_lid()
            if DRYRUN == False:
                profile_FRERAT = [
                    {'temperature': 32, 'hold_time_minutes': FRAGTIME},
                    {'temperature': 65, 'hold_time_minutes': 30}
                    ]
                thermocycler.execute_profile(steps=profile_FRERAT, repetitions=1, block_max_volume=50)
                thermocycler.set_block_temperature(4)
            ############################################################################################################################################
            thermocycler.open_lid()

        if STEP_LIG == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Adapter Ligation')
            protocol.comment('==============================================')
            #Standard Setup

            protocol.comment('--> Adding Lig')
            LIGVol = 30
            LIGMixRep = 30 if DRYRUN == False else 1
            LIGMixVol = 55
            for loop, X in enumerate(column_1_list):
                p1000.pick_up_tip()
                p1000.mix(3,LIGVol, LIG.bottom(z=0.5), rate=0.5) #original = .5
                p1000.aspirate(LIGVol, LIG.bottom(z=0.3), rate=0.2) #original = .3
                p1000.default_speed = 5
                p1000.move_to(LIG.top(5))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.dispense(LIGVol, sample_plate_1[X].bottom(z=0.3), rate=0.25) #original = .3
                p1000.move_to(sample_plate_1[X].bottom(z=0.5)) #original = .5
                p1000.mix(LIGMixRep,LIGMixVol, rate=0.5)
                p1000.blow_out(sample_plate_1[X].top(z=-1))
                protocol.delay(seconds=0.2)
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
                tipcheck()

        if STEP_LIGDECK == 1:
            ############################################################################################################################################
            protocol.comment('Seal, Run LIG (20min)')
            thermocycler.set_lid_temperature(37)    
            thermocycler.close_lid()
            if DRYRUN == False:
                profile_LIG = [
                    {'temperature': 20, 'hold_time_minutes': 20}
                    ]
                thermocycler.execute_profile(steps=profile_LIG, repetitions=1, block_max_volume=50)
                thermocycler.set_block_temperature(4)
            ############################################################################################################################################
            thermocycler.open_lid()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM THERMOCYCLER TO HEATERSHAKER
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

        if STEP_POSTLIG == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Cleanup 1')
            protocol.comment('==============================================')
            # Setting Labware to Resume at Cleanup 1
            if STEP_FRERAT == 0 and STEP_LIG == 0:
                #============================================================================================
                # GRIPPER MOVE sample_plate_1 FROM THERMOCYCLER TO HEATERSHAKER
                heatershaker.open_labware_latch()
                protocol.move_labware(
                    labware=sample_plate_1,
                    new_location=hs_adapter,
                    use_gripper=USE_GRIPPER,
                )
                heatershaker.close_labware_latch()
                #============================================================================================

            protocol.comment('--> ADDING AMPure (0.8x)')
            AMPureVol = 48
            SampleVol = 60
            AMPureMixRPM = 1800
            AirMultiDispense = False
            AMPureMixTime = 5*60 if DRYRUN == False else 0.1*60 # Seconds
            AMPurePremix = 3 if DRYRUN == False else 1
            #======== DISPENSE ===========
            if AirMultiDispense == True:
                p1000.pick_up_tip()
                p1000.mix(AMPurePremix,40, AMPure.bottom(z=1))
                for loop, X in enumerate(column_1_list):
                    p1000.aspirate(AMPureVol, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(AMPureVol, sample_plate_1[X].top(z=1), rate=1)
                    protocol.delay(seconds=0.2)
                    p1000.blow_out(sample_plate_1[X].top(z=-1))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
                tipcheck()
            else:
                for loop, X in enumerate(column_1_list):
                    p1000.pick_up_tip()
                    p1000.mix(AMPurePremix,AMPureVol+10, AMPure.bottom(z=1))
                    p1000.aspirate(AMPureVol, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(AMPureVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                    for Mix in range(2):
                        p1000.aspirate(50, rate=0.5)
                        p1000.move_to(sample_plate_1[X].bottom(z=1))
                        p1000.aspirate(30, rate=0.5)
                        p1000.dispense(30, rate=0.5)
                        p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                        p1000.dispense(50,rate=0.5)
                        Mix += 1
                    p1000.blow_out(sample_plate_1[X].top(z=2))
                    p1000.default_speed = 400
                    p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.move_to(sample_plate_1[X].top(z=0))
                    p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                    tipcheck()
            #==============================
            heatershaker.set_and_wait_for_shake_speed(rpm=AMPureMixRPM)
            protocol.delay(AMPureMixTime)
            heatershaker.deactivate_shaker()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM HEATER SHAKER TO MAG PLATE
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=mag_block,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            if DRYRUN == False:
                protocol.delay(minutes=4)

            protocol.comment('--> Removing Supernatant')
            RemoveSup = 200
            for loop, X in enumerate(column_1_list):
                p1000.pick_up_tip()
                p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                p1000.aspirate(RemoveSup-100, rate=0.25)
                protocol.delay(minutes=0.1)
                p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                p1000.aspirate(100, rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].top(z=2))
                p1000.default_speed = 200
                p1000.dispense(200, Liquid_trash.top(z=0), rate=0.5)
                protocol.delay(minutes=0.1)
                p1000.blow_out(Liquid_trash.top(z=-2))
                p1000.default_speed = 400
                p1000.move_to(Liquid_trash.top(z=-5))
                p1000.move_to(Liquid_trash.top(z=0))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
                tipcheck()
            
            for X in range(2):
                protocol.comment('--> ETOH Wash')
                ETOHMaxVol = 150
                AirMultiDispense = False
                #======== DISPENSE ===========
                if AirMultiDispense == True:
                    p1000.pick_up_tip()
                    for loop, X in enumerate(column_1_list):
                        p1000.aspirate(ETOHMaxVol, EtOH_1.bottom(z=1))
                        p1000.move_to(EtOH_1.top(z=0))
                        p1000.move_to(EtOH_1.top(z=-5))
                        p1000.move_to(EtOH_1.top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out(sample_plate_1[X].top(z=-2))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                    tipcheck()
                else:
                    for loop, X in enumerate(column_1_list):
                        p1000.pick_up_tip()
                        p1000.aspirate(ETOHMaxVol, EtOH_1.bottom(z=1))
                        p1000.move_to(EtOH_1.top(z=0))
                        p1000.move_to(EtOH_1.top(z=-5))
                        p1000.move_to(EtOH_1.top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out()
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                        p200_tips += 1
                        tipcheck()                    
                #==============================
                if DRYRUN == False:
                    protocol.delay(minutes=0.5)
                
                protocol.comment('--> Remove ETOH Wash')
                for loop, X in enumerate(column_1_list):
                    p1000.pick_up_tip()
                    p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                    p1000.aspirate(RemoveSup-100, rate=0.25)
                    protocol.delay(minutes=0.1)
                    p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                    p1000.aspirate(100, rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].top(z=2))
                    p1000.default_speed = 200
                    p1000.dispense(200, Liquid_trash.top(z=0))
                    protocol.delay(minutes=0.1)
                    p1000.blow_out()
                    p1000.default_speed = 400
                    p1000.move_to(Liquid_trash.top(z=-5))
                    p1000.move_to(Liquid_trash.top(z=0))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                    tipcheck()

            if DRYRUN == False:
                protocol.delay(minutes=1)

            protocol.comment('--> Removing Residual Wash')
            for loop, X in enumerate(column_1_list):
                p50.pick_up_tip() #<---------------- Tip Pickup
                p50.move_to(sample_plate_1[X].bottom(1))
                p50.aspirate(20, rate=0.25)
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()

            if DRYRUN == False:
                protocol.delay(minutes=0.5)

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM MAG PLATE TO HEATER SHAKER
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            protocol.comment('--> Adding RSB')
            RSBVol = 22
            RSBMixRPM = 2000
            AirMultiDispense = False
            RSBMixRep = 5*60 if DRYRUN == False else 0.1*60
            #======== DISPENSE ===========
            if AirMultiDispense == True:
                p50.pick_up_tip()
                for loop, X in enumerate(column_1_list):
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].top(z=3))
                    p50.dispense(RSBVol, rate=2)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top(z=3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()
            else:
                for loop, X in enumerate(column_1_list):
                    p50.pick_up_tip() #<---------------- Tip Pickup
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].bottom(z=1))
                    p50.dispense(RSBVol, rate=1)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top())
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
                    tipcheck()
            #===============================
            heatershaker.set_and_wait_for_shake_speed(rpm=RSBMixRPM)
            protocol.delay(RSBMixRep)
            heatershaker.deactivate_shaker()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM HEATERSHAKER TO MAG PLATE
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=mag_block,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            if DRYRUN == False:
                protocol.delay(minutes=4)

            protocol.comment('--> Transferring Supernatant')
            TransferSup = 20
            for loop, X in enumerate(column_1_list):
                p50.pick_up_tip()
                p50.move_to(sample_plate_1[X].bottom(z=0.75))
                p50.aspirate(TransferSup, rate=0.25)
                p50.dispense(TransferSup+5, sample_plate_1[column_2_list[loop]].bottom(z=1))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM MAG PLATE to THERMOCYCLER
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=thermocycler,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

        if STEP_PCR == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Amplification')
            protocol.comment('==============================================')
            #Standard Setup

            Liquid_trash = Liquid_trash_well_2

            protocol.comment('--> Adding Barcodes')
            BarcodeVol    = 5
            BarcodeMixRep = 3 if DRYRUN == False else 1
            BarcodeMixVol = 10
            for loop, X in enumerate(column_2_list):
                p50.pick_up_tip()
                p50.aspirate(BarcodeVol, reagent_plate.wells_by_name()[barcodes[loop]].bottom(.3), rate=0.25) #original = ()
                p50.dispense(BarcodeVol, sample_plate_1.wells_by_name()[X].bottom(1))
                p50.mix(BarcodeMixRep,BarcodeMixVol)
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()

            protocol.comment('--> Adding PCR')
            PCRVol    = 25
            PCRMixRep = 10 if DRYRUN == False else 1
            PCRMixVol = 50
            for loop, X in enumerate(column_2_list):
                p50.pick_up_tip()
                p50.mix(2,PCRVol, PCR.bottom(.3), rate=0.5) #original = ()
                p50.aspirate(PCRVol, PCR.bottom(.3), rate=0.25) #original = ()
                p50.dispense(PCRVol, sample_plate_1[X].bottom(.3), rate=0.25) #original = ()
                p50.mix(PCRMixRep, PCRMixVol, rate=1)
                p50.move_to(sample_plate_1[X].bottom(.3)) #original = ()
                protocol.delay(minutes=0.1)
                p50.blow_out(sample_plate_1[X].top(z=-5))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()

        if STEP_PCRDECK == 1:
            ############################################################################################################################################
            if DRYRUN == False:
                thermocycler.set_lid_temperature(105)
            thermocycler.close_lid()
            if DRYRUN == False:
                profile_PCR_1 = [
                    {'temperature': 98, 'hold_time_seconds': 45}
                    ]
                thermocycler.execute_profile(steps=profile_PCR_1, repetitions=1, block_max_volume=50)
                profile_PCR_2 = [
                    {'temperature': 98, 'hold_time_seconds': 15},
                    {'temperature': 60, 'hold_time_seconds': 30},
                    {'temperature': 72, 'hold_time_seconds': 30}
                    ]
                thermocycler.execute_profile(steps=profile_PCR_2, repetitions=PCRCYCLES, block_max_volume=50)
                profile_PCR_3 = [
                    {'temperature': 72, 'hold_time_minutes': 1}
                    ]
                thermocycler.execute_profile(steps=profile_PCR_3, repetitions=1, block_max_volume=50)
                thermocycler.set_block_temperature(4)
            ############################################################################################################################################
            thermocycler.open_lid()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM THERMOCYCLER TO HEATERSHAKER
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

        if STEP_POSTPCR == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Cleanup 2')
            protocol.comment('==============================================')
             # Setting Labware to Resume at Cleanup 2           
            if STEP_FRERAT == 0 and STEP_LIG == 0 and STEP_POSTLIG == 0 and STEP_PCR == 0:
                #============================================================================================
                # GRIPPER MOVE sample_plate_1 FROM THERMOCYCLER TO HEATERSHAKER
                heatershaker.open_labware_latch()
                protocol.move_labware(
                    labware=sample_plate_1,
                    new_location=hs_adapter,
                    use_gripper=USE_GRIPPER,
                )
                heatershaker.close_labware_latch()
                #============================================================================================

            protocol.comment('--> ADDING AMPure (0.65x)')
            AMPureVol = 32.5
            SampleVol = 50
            AMPureMixRPM = 1800
            AirMultiDispense = False
            AMPureMixTime = 5*60 if DRYRUN == False else 0.1*60 # Seconds
            AMPurePremix = 3 if DRYRUN == False else 1
            #======== DISPENSE ===========
            if AirMultiDispense == True:
                p1000.pick_up_tip()
                p1000.mix(AMPurePremix,40, AMPure.bottom(z=1))
                for loop, X in enumerate(column_2_list):
                    p1000.aspirate(AMPureVol, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(AMPureVol, sample_plate_1[X].top(z=1), rate=1)
                    protocol.delay(seconds=0.2)
                    p1000.blow_out(sample_plate_1[X].top(z=-1))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
                tipcheck()
            else:
                for loop, X in enumerate(column_2_list):
                    p1000.pick_up_tip()
                    p1000.aspirate(AMPureVol, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(AMPureVol, sample_plate_1[X].top(z=1), rate=1)
                    protocol.delay(seconds=0.2)
                    p1000.blow_out(sample_plate_1[X].top(z=-1))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                    tipcheck()
            #==============================
            heatershaker.set_and_wait_for_shake_speed(rpm=AMPureMixRPM)
            protocol.delay(AMPureMixTime)
            heatershaker.deactivate_shaker()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM HEATER SHAKER TO MAG PLATE
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=mag_block,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            if DRYRUN == False:
                protocol.delay(minutes=4)

            protocol.comment('--> Removing Supernatant')
            RemoveSup = 200
            for loop, X in enumerate(column_2_list):
                p1000.pick_up_tip() #<---------------- Tip Pickup
                p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                p1000.aspirate(RemoveSup-100, rate=0.25)
                protocol.delay(minutes=0.1)
                p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                p1000.aspirate(100, rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].top(z=2))
                p1000.default_speed = 200
                p1000.dispense(200, Liquid_trash.top(z=0))
                protocol.delay(minutes=0.1)
                p1000.blow_out()
                p1000.default_speed = 400
                p1000.move_to(Liquid_trash.top(z=-5))
                p1000.move_to(Liquid_trash.top(z=0))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
                tipcheck()

            for X in range(2):
                protocol.comment('--> ETOH Wash')
                ETOHMaxVol = 150
                AirMultiDispense = False
                #======== DISPENSE ===========
                if AirMultiDispense == True:
                    p1000.pick_up_tip()
                    for loop, X in enumerate(column_2_list):
                        p1000.aspirate(ETOHMaxVol, EtOH_2.bottom(z=1))
                        p1000.move_to(EtOH_2.top(z=0))
                        p1000.move_to(EtOH_2.top(z=-5))
                        p1000.move_to(EtOH_2.top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out(sample_plate_1[X].top(z=-2))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                    tipcheck()
                else:
                    for loop, X in enumerate(column_2_list):
                        p1000.pick_up_tip()
                        p1000.aspirate(ETOHMaxVol, EtOH_2.bottom(z=1))
                        p1000.move_to(EtOH_2.top(z=0))
                        p1000.move_to(EtOH_2.top(z=-5))
                        p1000.move_to(EtOH_2.top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out()
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                        p200_tips += 1
                        tipcheck()
                #==============================
                if DRYRUN == False:
                    protocol.delay(minutes=0.5)
                
                protocol.comment('--> Remove ETOH Wash')
                for loop, X in enumerate(column_2_list):
                    p1000.pick_up_tip()
                    p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                    p1000.aspirate(RemoveSup-100, rate=0.25)
                    protocol.delay(minutes=0.1)
                    p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                    p1000.aspirate(100, rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].top(z=2))
                    p1000.default_speed = 200
                    p1000.dispense(200, Liquid_trash.top(z=0))
                    protocol.delay(minutes=0.1)
                    p1000.blow_out()
                    p1000.default_speed = 400
                    p1000.move_to(Liquid_trash.top(z=-5))
                    p1000.move_to(Liquid_trash.top(z=0))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                    tipcheck()

            if DRYRUN == False:
                protocol.delay(minutes=1)

            protocol.comment('--> Removing Residual Wash')
            for loop, X in enumerate(column_2_list):
                p50.pick_up_tip() #<---------------- Tip Pickup
                p50.move_to(sample_plate_1[X].bottom(1))
                p50.aspirate(20, rate=0.25)
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()

            if DRYRUN == False:
                protocol.delay(minutes=0.5)

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM MAG PLATE TO HEATER SHAKER
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            protocol.comment('--> Adding RSB')
            RSBVol = 22        
            RSBMixRPM = 2000
            AirMultiDispense = False
            RSBMixRep = 5*60 if DRYRUN == False else 0.1*60
            #======== DISPENSE ===========
            if AirMultiDispense == True:
                p50.pick_up_tip()
                for loop, X in enumerate(column_2_list):
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].top(z=3))
                    p50.dispense(RSBVol, rate=2)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top(z=3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                tipcheck()
            else:
                for loop, X in enumerate(column_2_list):
                    p50.pick_up_tip() #<---------------- Tip Pickup
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].bottom(z=1))
                    p50.dispense(RSBVol, rate=1)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top())
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
                    tipcheck()
            #==============================
            heatershaker.set_and_wait_for_shake_speed(rpm=RSBMixRPM)
            protocol.delay(RSBMixRep)
            heatershaker.deactivate_shaker()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM HEATER SHAKER TO MAG PLATE
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=mag_block,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            if DRYRUN == False:
                protocol.delay(minutes=4)

            protocol.comment('--> Transferring Supernatant')
            TransferSup = 20
            for loop, X in enumerate(column_2_list):
                p1000.pick_up_tip() #<---------------- Tip Pickup
                p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                p1000.aspirate(TransferSup, rate=0.25)
                p1000.dispense(TransferSup+5, sample_plate_1[column_3_list[loop]].bottom(z=1))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
                tipcheck()

        if ABR_TEST == True:
            protocol.comment('==============================================')
            protocol.comment('--> Resetting Run')
            protocol.comment('==============================================')

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM MAG PLATE To Thermocycler
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=thermocycler,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================

            p1000.pick_up_tip()
            # Resetting FRERAT
            p1000.aspirate(COLUMNS*10.5, Liquid_trash_well_1.bottom(z=1))
            p1000.dispense(COLUMNS*10.5, FRERAT.bottom(z=1))
            # Resetting LIG
            p1000.aspirate(COLUMNS*30, Liquid_trash_well_1.bottom(z=1))
            p1000.dispense(COLUMNS*30, LIG.bottom(z=1))
            # Resetting ETOH
            for X in range(COLUMNS):
                p1000.aspirate(150, Liquid_trash_well_1.bottom(z=1))
                p1000.dispense(150, EtOH_1.bottom(z=1))
                p1000.aspirate(150, Liquid_trash_well_1.bottom(z=1))
                p1000.dispense(150, EtOH_1.bottom(z=1))

                p1000.aspirate(150, Liquid_trash_well_2.bottom(z=1))
                p1000.dispense(150, EtOH_2.bottom(z=1))
                p1000.aspirate(150, Liquid_trash_well_2.bottom(z=1))
                p1000.dispense(150, EtOH_2.bottom(z=1))
            # Resetting AMPURE
            for X in range(COLUMNS):
                p1000.aspirate(COLUMNS*48, Liquid_trash_well_1.bottom(z=1))
                p1000.dispense(COLUMNS*48, AMPure.bottom(z=1))
            for X in range(COLUMNS):
                p1000.aspirate(COLUMNS*50, Liquid_trash_well_2.bottom(z=1))
                p1000.dispense(COLUMNS*50, AMPure.bottom(z=1))
            # Resetting PCR
            p1000.aspirate(COLUMNS*25, Liquid_trash_well_2.bottom(z=1))
            p1000.dispense(COLUMNS*25, PCR.bottom(z=1))
            p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
            # Resetting RSB
            p1000.aspirate(COLUMNS*22, Liquid_trash_well_1.bottom(z=1))
            p1000.dispense(COLUMNS*22, RSB.bottom(z=1))
            p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
            p200_tips += 1
            tipcheck()

            p50.pick_up_tip()
            # Removing Final Samples
            for loop, X in enumerate(column_3_list):
                p50.aspirate(20, sample_plate_1[X].bottom(z=1))
                p50.dispense(20, Liquid_trash_well_1.bottom(z=1))
            # Resetting Initial Samples
            for loop, X in enumerate(column_1_list):
                p50.aspirate(19.5, Liquid_trash_well_1.bottom(z=1))
                p50.dispense(19.5, sample_plate_1[X].bottom(z=1))
            # Resetting Barcodes
            for loop, X in enumerate(barcodes):
                p50.aspirate(5, Liquid_trash_well_2.bottom(z=1))
                p50.dispense(5, sample_plate_1[X].bottom(z=1))
            
            p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
            p50_tips += 1
            tipcheck()