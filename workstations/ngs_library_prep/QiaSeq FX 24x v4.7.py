from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'Qiaseq FX 24x v4.7',
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
COLUMNS             = 3            # 1-3
FRAGTIME            = 15            # Minutes, Duration of the Fragmentation Step
PCRCYCLES           = 6             # Amount of Cycles
RES_TYPE            = '12x15ml'     # '12x15ml' or '96x2ml'
ETOH_1_AirMultiDis    = False
RSB_1_AirMultiDis     = False
ETOH_2_AirMultiDis    = False
RSB_2_AirMultiDis     = False
AMP_3_AirMultiDis     = False
ETOH_3_AirMultiDis    = False
RSB_3_AirMultiDis     = False

# PROTOCOL BLOCKS
STEP_FX             = 1
STEP_FXDECK         = 1
STEP_LIG            = 1
STEP_LIGDECK        = 1
STEP_CLEANUP_1      = 1
STEP_CLEANUP_2      = 1
STEP_PCR            = 1
STEP_PCRDECK        = 1
STEP_CLEANUP_3      = 1

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

p200_tips           = 0
p50_tips            = 0
WasteVol            = 0
Resetcount          = 0

ABR_TEST            = False
if ABR_TEST == True:
    COLUMNS         = 3              # Overrides to 3 columns
    DRYRUN          = True           # Overrides to only DRYRUN
    TIP_TRASH       = False          # Overrides to only REUSING TIPS
    RUN             = 1              # Repetitions
else:
    RUN             = 1

def run(protocol: protocol_api.ProtocolContext):

    global p200_tips
    global p50_tips
    global WasteVol
    global Resetcount

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
    tiprack_200_3        = protocol.load_labware('opentrons_flex_96_tiprack_200ul','B3')
    # ========== FOURTH ROW ==========
    tiprack_200_4       = protocol.load_labware('opentrons_flex_96_tiprack_200ul',  'A2')
 
    # =========== RESERVOIR ==========
    AMPure              = reservoir['A1']    
    EtOH_1              = reservoir['A3']
    EtOH_2              = reservoir['A4']
    EtOH_3              = reservoir['A5']
    RSB                 = reservoir['A7']
    Liquid_trash_well_1 = reservoir['A10']
    Liquid_trash_well_2 = reservoir['A11']
    Liquid_trash_well_3 = reservoir['A12']

    # ========= REAGENT PLATE ==========
    FX                  = reagent_plate.wells_by_name()['A1']
    LIG                 = reagent_plate.wells_by_name()['A2']
    Primer              = reagent_plate.wells_by_name()['A3']
    PCR                 = reagent_plate.wells_by_name()['A4']
    Barcodes_1          = reagent_plate.wells_by_name()['A7']
    Barcodes_2          = reagent_plate.wells_by_name()['A8']
    Barcodes_3          = reagent_plate.wells_by_name()['A9']

    # pipette
    p1000 = protocol.load_instrument("flex_8channel_1000", "left",tip_racks=[tiprack_200_1,tiprack_200_2,tiprack_200_3,tiprack_200_4])
    p50 = protocol.load_instrument("flex_8channel_50", "right",tip_racks=[tiprack_50_1])
    p200_tipracks = 4
    p50_tipracks = 1

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
        global p200_tips
        global p50_tips
        global Resetcount
        if p200_tips == p200_tipracks*12:
            if ABR_TEST == True: 
                p1000.reset_tipracks()
            else:
                protocol.pause('RESET p200 TIPS')
                p1000.reset_tipracks()
            Resetcount += 1
            p200_tips = 0 
        if p50_tips == p50_tipracks*12:
            if ABR_TEST == True: 
                p50.reset_tipracks()
            else:
                protocol.pause('RESET p50 TIPS')
                p50.reset_tipracks()
            Resetcount += 1
            p50_tips = 0

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
            thermocycler.set_lid_temperature(100)    
            temp_block.set_temperature(4)
        protocol.pause("Ready")
        heatershaker.close_labware_latch()
        Liquid_trash = Liquid_trash_well_1

        # Sample Plate contains 100ng of DNA in 19.5ul Low EDTA TE

        if STEP_FX == 1:
            protocol.comment('==============================================')
            protocol.comment('--> FX')
            protocol.comment('==============================================')

            protocol.comment('--> Adding FX')
            FXBuffVol    = 15
            FXBuffPremix = 2 if DRYRUN == False else 1
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p50.pick_up_tip()
                p50.mix(FXBuffPremix,FXBuffVol+3, FX.bottom(z=1))
                p50.aspirate(FXBuffVol+3, FX.bottom(z=1))
                p50.dispense(3, FX.bottom(z=1))
                p50.dispense(FXBuffVol, sample_plate_1.wells_by_name()[X].bottom(z=1)) #Changed FXBuffVol+1 to FXBuffVol
                p50.move_to(sample_plate_1[X].top(z=-3))
                protocol.delay(minutes=0.1)
                p50.blow_out(sample_plate_1[X].top(z=-3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================

        if STEP_FXDECK == 1:
            ############################################################################################################################################
            thermocycler.close_lid()
            if DRYRUN == False:
                profile_FX = [
                    {'temperature': 32, 'hold_time_minutes': FRAGTIME},
                    {'temperature': 65, 'hold_time_minutes': 30}
                    ]
                thermocycler.execute_profile(steps=profile_FX, repetitions=1, block_max_volume=50)
                thermocycler.set_block_temperature(4)
            ############################################################################################################################################
            thermocycler.open_lid()

        if STEP_LIG == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Adapter Ligation')
            protocol.comment('==============================================')

            '''
            if COLUMNS == 3:
                protocol.comment('--> Adding Lig and Barcodes')
                LIGVol = 45
                LIGMixRep = 20
                LIGMixVol = 45
                BarcodeVol    = 5
                BarcodeMixRep = 3 if DRYRUN == False else 1
                BarcodeMixVol = 10
                for loop, X in enumerate(column_1_list):
                    tipcheck()
                    p1000.pick_up_tip()
                    protocol.comment('--> Adding Lig')
                    p1000.aspirate(LIGVol, LIG.bottom(z=1), rate=0.2)
                    p1000.default_speed = 5
                    p1000.move_to(LIG.top(z=5))
                    protocol.delay(seconds=0.2)
                    p1000.default_speed = 400
                    protocol.comment('--> Adding Barcodes')
                    p1000.aspirate(BarcodeVol, reagent_plate.wells_by_name()[barcodes[loop]].bottom(), rate=0.25)
                    p1000.dispense(LIGVol+BarcodeVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                    p1000.move_to(sample_plate_1[X].bottom(z=1))
                    p1000.mix(LIGMixRep,LIGMixVol, rate=0.5)
                    p1000.blow_out(sample_plate_1[X].top(z=-5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
            else:
            '''
            protocol.comment('--> Adding Barcodes')
            BarcodeVol    = 5
            BarcodeMixRep = 3 if DRYRUN == False else 1
            BarcodeMixVol = 10
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p50.pick_up_tip()
                p50.aspirate(BarcodeVol+3, reagent_plate.wells_by_name()[barcodes[loop]].bottom(.7), rate=0.25)
                p50.dispense(3, reagent_plate.wells_by_name()[barcodes[loop]].bottom(.7), rate=0.25)
                p50.dispense(BarcodeVol, sample_plate_1.wells_by_name()[X].bottom(1)) #Changed BarcodeVol+2 to BarcodeVol
                p50.mix(BarcodeMixRep,BarcodeMixVol)
                p50.move_to(sample_plate_1[X].top(z=-3))
                protocol.delay(minutes=0.1)
                p50.blow_out(sample_plate_1[X].top(z=-3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================

            protocol.comment('--> Adding Lig')
            LIGVol = 45
            LIGMixRep = 20
            LIGMixVol = 90
            LIGMixPremix = 3 if DRYRUN == False else 1
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p1000.pick_up_tip()
                p1000.mix(LIGMixPremix,LIGVol+3, LIG.bottom(z=1))
                p1000.aspirate(LIGVol+3, LIG.bottom(z=1), rate=0.2)
                p1000.dispense(3, LIG.bottom(z=1), rate=0.2)
                p1000.default_speed = 5
                p1000.move_to(LIG.top(z=5))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.dispense(LIGVol, sample_plate_1[X].bottom(z=1), rate=0.25) #changed LIGVol+2 to LIGVol
                p1000.move_to(sample_plate_1[X].bottom(z=1))
                p1000.mix(LIGMixRep,LIGMixVol, rate=0.5)
                p1000.move_to(sample_plate_1[X].top(z=-3))
                protocol.delay(minutes=0.1)
                p1000.blow_out(sample_plate_1[X].top(z=-3))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================

        if STEP_LIGDECK == 1:
            ############################################################################################################################################
            thermocycler.close_lid()
            if DRYRUN == False:
                profile_LIG = [
                    {'temperature': 20, 'hold_time_minutes': 15}
                    ]
                thermocycler.execute_profile(steps=profile_LIG, repetitions=1, block_max_volume=50)
                thermocycler.set_block_temperature(10)
            ############################################################################################################################################
            thermocycler.open_lid()

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM THERMOCYCLER TO HEATER SHAKER
            heatershaker.open_labware_latch()    
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()    
            #============================================================================================
        
        if STEP_CLEANUP_1 == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Cleanup 1')
            protocol.comment('==============================================')
            # Setting Labware to Resume at Cleanup 1
            if STEP_FX == 0 and STEP_LIG == 0:
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
            AMPureVol = 80
            SampleVol = 100
            AMPureMixRPM = 500
            AMPureMixTime = 6*60 if DRYRUN == False else 0.1*60
            AMPurePremix = 3 if DRYRUN == False else 1
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p1000.pick_up_tip()
                p1000.mix(AMPurePremix,AMPureVol+3, AMPure.bottom(z=1))
                p1000.aspirate(AMPureVol+3, AMPure.bottom(z=1), rate=0.25)
                p1000.dispense(3, AMPure.bottom(z=1), rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(AMPure.top(z=-3))
                p1000.default_speed = 100
                p1000.move_to(AMPure.top().move(types.Point(x=4,z=-3)))
                p1000.move_to(AMPure.top().move(types.Point(x=-4,z=-3)))
                p1000.default_speed = 400                
                p1000.dispense(AMPureVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].bottom(z=5))
                for Mix in range(5):
                    p1000.aspirate(70, rate=0.5)
                    p1000.move_to(sample_plate_1[X].bottom(z=1))
                    p1000.aspirate(70, rate=0.5)
                    p1000.dispense(70, rate=0.5)
                    p1000.move_to(sample_plate_1[X].bottom(z=6))
                    p1000.dispense(70,rate=0.5)
                    Mix += 1
                p1000.move_to(sample_plate_1[X].top(z=-3))
                protocol.delay(seconds=0.2)
                p1000.blow_out(sample_plate_1[X].top(z=-3))
                p1000.touch_tip(speed=100)
                p1000.default_speed = 400
                p1000.move_to(sample_plate_1[X].top(z=5))
                p1000.move_to(sample_plate_1[X].top(z=0))
                p1000.move_to(sample_plate_1[X].top(z=5))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================
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
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p1000.pick_up_tip()
                p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                p1000.aspirate(RemoveSup-100, rate=0.25)
                protocol.delay(minutes=0.1)
                p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                p1000.aspirate(100, rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].top(z=-2))
                p1000.default_speed = 200
                p1000.touch_tip(speed=100)
                p1000.dispense(200, Liquid_trash.top(z=-3))
                protocol.delay(minutes=0.1)
                p1000.blow_out()
                p1000.default_speed = 100
                p1000.move_to(Liquid_trash.top().move(types.Point(x=4,z=-3)))
                p1000.move_to(Liquid_trash.top().move(types.Point(x=-4,z=-3)))
                p1000.default_speed = 400
                p1000.move_to(Liquid_trash.top(z=-5))
                p1000.move_to(Liquid_trash.top(z=0))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================

            for X in range(2):
                protocol.comment('--> ETOH Wash')
                ETOHMaxVol = 150
                #===============================================
                if ETOH_1_AirMultiDis == True:
                    tipcheck()
                    p1000.pick_up_tip()
                    for loop, X in enumerate(column_1_list):
                        p1000.aspirate(ETOHMaxVol, EtOH_1.bottom(z=1))
                        p1000.move_to(EtOH_1.top(z=0))
                        p1000.move_to(EtOH_1.top(z=-5))
                        p1000.default_speed = 100
                        p1000.move_to(EtOH_1.top().move(types.Point(x=4,z=-3)))
                        p1000.move_to(EtOH_1.top().move(types.Point(x=-4,z=-3)))
                        p1000.default_speed = 400                
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out(sample_plate_1[X].top(z=-2))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                else:
                    for loop, X in enumerate(column_1_list):
                        tipcheck()
                        p1000.pick_up_tip()
                        p1000.aspirate(ETOHMaxVol, EtOH_1.bottom(z=1))
                        p1000.move_to(EtOH_1.top(z=0))
                        p1000.move_to(EtOH_1.top(z=-5))
                        p1000.default_speed = 100
                        p1000.move_to(EtOH_1.top().move(types.Point(x=4,z=-3)))
                        p1000.move_to(EtOH_1.top().move(types.Point(x=-4,z=-3)))
                        p1000.default_speed = 400                
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out()
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                        p200_tips += 1
                    #===============================================

                if DRYRUN == False:
                    protocol.delay(minutes=0.5)

                protocol.comment('--> Remove ETOH Wash')
                #===============================================
                for loop, X in enumerate(column_1_list):
                    tipcheck()
                    p1000.pick_up_tip()
                    p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                    p1000.aspirate(RemoveSup-100, rate=0.25)
                    protocol.delay(minutes=0.1)
                    p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                    p1000.aspirate(100, rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].top(z=-2))
                    p1000.default_speed = 200
                    p1000.touch_tip(speed=100)
                    p1000.dispense(200, Liquid_trash.top(z=-3))
                    protocol.delay(minutes=0.1)
                    p1000.blow_out()
                    p1000.default_speed = 100
                    p1000.move_to(Liquid_trash.top().move(types.Point(x=4,z=-3)))
                    p1000.move_to(Liquid_trash.top().move(types.Point(x=-4,z=-3)))
                    p1000.default_speed = 400
                    p1000.move_to(Liquid_trash.top(z=-5))
                    p1000.move_to(Liquid_trash.top(z=0))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                #===============================================

            '''
            if COLUMNS == 3:
                if DRYRUN == False:
                    protocol.delay(minutes=3)

            else:
            '''
            if DRYRUN == False:
                protocol.delay(minutes=1)

            protocol.comment('--> Removing Residual Wash')
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p50.pick_up_tip()
                p50.move_to(sample_plate_1[X].bottom(1))
                p50.aspirate(20, rate=0.25)
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================

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
            RSBVol = 50
            RSBMixRPM = 2000
            RSBMixTime = 5*60 if DRYRUN == False else 0.1*60
            #===============================================
            if RSB_1_AirMultiDis == True:
                tipcheck()
                p50.pick_up_tip()
                for loop, X in enumerate(column_1_list):
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].top(z=-3))
                    p50.dispense(RSBVol, rate=2)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top(z=-3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            else:
                for loop, X in enumerate(column_1_list):
                    tipcheck()
                    p50.pick_up_tip()
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].bottom(z=1))
                    p50.dispense(RSBVol, rate=1)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top(z=-3))
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
            #===============================================
            heatershaker.set_and_wait_for_shake_speed(rpm=RSBMixRPM)
            protocol.delay(RSBMixTime)
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
                protocol.delay(minutes=3)

            '''
            if COLUMNS == 3:
                protocol.comment('--> ADDING AMPure (0.8x)')
                AMPureVol = 50
                SampleVol = 50
                TransferSup = 50
                AMPureMixRPM = 1800
                AMPureMixTime = 5*60 if DRYRUN == False else 0.1*60
                AMPurePremix = 3 if DRYRUN == False else 1
                #===============================================
                for loop, X in enumerate(column_2_list):
                    protocol.comment('--> ADDING AMPure (0.8x)')
                    tipcheck()
                    p1000.pick_up_tip()
                    p1000.mix(AMPurePremix,AMPureVol+10, AMPure.bottom(z=1))
                    p1000.aspirate(AMPureVol, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(AMPureVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                    protocol.comment('--> Transferring Supernatant')
                    p1000.move_to(sample_plate_1[column_1_list[loop]].bottom(z=0.3))
                    p1000.aspirate(TransferSup+2, rate=0.25)
                    p1000.dispense(TransferSup+5, sample_plate_1[column_2_list[loop]].bottom(z=1))
                    p1000.move_to(sample_plate_1[X].bottom(z=5))
                    for Mix in range(2):
                        p1000.aspirate(50, rate=0.5)
                        p1000.move_to(sample_plate_1[X].bottom(z=1))
                        p1000.aspirate(20, rate=0.5)
                        p1000.dispense(20, rate=0.5)
                        p1000.move_to(sample_plate_1[X].bottom(z=5))
                        p1000.dispense(50,rate=0.5)
                        Mix += 1
                    p1000.move_to(sample_plate_1[X].top(z=-3))
                    protocol.delay(seconds=0.2)
                    p1000.blow_out(sample_plate_1[X].top(z=-3))
                    p1000.default_speed = 400
                    p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.move_to(sample_plate_1[X].top(z=0))
                    p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                #===============================================
                heatershaker.set_and_wait_for_shake_speed(rpm=AMPureMixRPM)
                protocol.delay(AMPureMixTime)
                heatershaker.deactivate_shaker()

                #============================================================================================
                # GRIPPER MOVE sample_plate_1 FROM MAG PLATE TO HEATERSHAKER
                heatershaker.open_labware_latch()
                protocol.move_labware(
                    labware=sample_plate_1,
                    new_location=hs_adapter,
                    use_gripper=USE_GRIPPER,
                )
                heatershaker.close_labware_latch()
                #============================================================================================

            else:
            '''
            protocol.comment('--> Transferring Supernatant')
            TransferSup = 50
            #===============================================
            for loop, X in enumerate(column_1_list):
                tipcheck()
                p50.pick_up_tip()
                p50.move_to(sample_plate_1[X].bottom(z=0.4))
                p50.aspirate(TransferSup/2, rate=0.25)
                protocol.delay(seconds=0.2)
                p50.move_to(sample_plate_1[X].bottom(z=0.4))
                p50.aspirate(TransferSup/2, rate=0.25)
                p50.dispense(TransferSup, sample_plate_1[column_2_list[loop]].bottom(z=1)) #Changed TransferSup+3 to TransferSup
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM MAG PLATE TO HEATERSHAKER
            heatershaker.open_labware_latch()
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()
            #============================================================================================


        if STEP_CLEANUP_2 == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Cleanup 2')
            protocol.comment('==============================================')
        
            Liquid_trash = Liquid_trash_well_2

            '''
            if COLUMNS == 3:
                protocol.delay(minutes=0.1)

            else:
            '''
            protocol.delay(minutes=0.1)

            protocol.comment('--> ADDING AMPure (0.8x)')
            AMPureVol = 50
            SampleVol = 50
            AMPureMixRPM = 1800
            AMPureMixTime = 5*60 if DRYRUN == False else 0.1*60
            AMPurePremix = 3 if DRYRUN == False else 1
            #===============================================
            for loop, X in enumerate(column_2_list):
                tipcheck()
                p1000.pick_up_tip()
                p1000.mix(AMPurePremix,AMPureVol+3, AMPure.bottom(z=1))
                p1000.aspirate(AMPureVol+3, AMPure.bottom(z=1), rate=0.25)
                p1000.dispense(3, AMPure.bottom(z=1), rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(AMPure.top(z=-3))
                p1000.default_speed = 100
                p1000.move_to(AMPure.top().move(types.Point(x=4,z=-3)))
                p1000.move_to(AMPure.top().move(types.Point(x=-4,z=-3)))
                p1000.default_speed = 400 
                p1000.dispense(AMPureVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].bottom(z=5))
                for Mix in range(2):
                    p1000.aspirate(50, rate=0.5)
                    p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                    p1000.aspirate(20, rate=0.5)
                    p1000.dispense(20, rate=0.5)
                    p1000.move_to(sample_plate_1[X].bottom(z=3))
                    p1000.dispense(50,rate=0.5)
                    Mix += 1
                p1000.move_to(sample_plate_1[X].top(z=-3))
                protocol.delay(seconds=0.2)
                p1000.blow_out(sample_plate_1[X].top(z=-3))
                p1000.touch_tip(speed=100)
                p1000.default_speed = 400
                p1000.move_to(sample_plate_1[X].top(z=5))
                p1000.move_to(sample_plate_1[X].top(z=0))
                p1000.move_to(sample_plate_1[X].top(z=5))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================
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
            #===============================================
            for loop, X in enumerate(column_2_list):
                tipcheck()
                p1000.pick_up_tip()
                p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                p1000.aspirate(RemoveSup-100, rate=0.25)
                protocol.delay(minutes=0.1)
                p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                p1000.aspirate(100, rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].top(z=-2))
                p1000.default_speed = 200
                p1000.touch_tip(speed=100)
                p1000.dispense(200, Liquid_trash.top(z=-3))
                protocol.delay(minutes=0.1)
                p1000.blow_out()
                p1000.default_speed = 100
                p1000.move_to(Liquid_trash.top().move(types.Point(x=4,z=-3)))
                p1000.move_to(Liquid_trash.top().move(types.Point(x=-4,z=-3)))
                p1000.default_speed = 400
                p1000.move_to(Liquid_trash.top(z=-5))
                p1000.move_to(Liquid_trash.top(z=0))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================
            
            for X in range(2):
                protocol.comment('--> ETOH Wash')
                ETOHMaxVol = 150
                #===============================================
                if ETOH_2_AirMultiDis == True:
                    tipcheck()
                    p1000.pick_up_tip()
                    for loop, X in enumerate(column_2_list):
                        p1000.aspirate(ETOHMaxVol, EtOH_2.bottom(z=1))
                        p1000.move_to(EtOH_2.top(z=0))
                        p1000.move_to(EtOH_2.top(z=-5))
                        p1000.default_speed = 100
                        p1000.move_to(EtOH_2.top().move(types.Point(x=4,z=-3)))
                        p1000.move_to(EtOH_2.top().move(types.Point(x=-4,z=-3)))
                        p1000.default_speed = 400
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out(sample_plate_1[X].top(z=-2))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                else:
                    for loop, X in enumerate(column_2_list):
                        tipcheck()
                        p1000.pick_up_tip()
                        p1000.aspirate(ETOHMaxVol, EtOH_2.bottom(z=1))
                        p1000.move_to(EtOH_2.top(z=0))
                        p1000.move_to(EtOH_2.top(z=-5))
                        p1000.default_speed = 100
                        p1000.move_to(EtOH_2.top().move(types.Point(x=4,z=-3)))
                        p1000.move_to(EtOH_2.top().move(types.Point(x=-4,z=-3)))
                        p1000.default_speed = 400
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out()
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                        p200_tips += 1
                #===============================================
                if DRYRUN == False:
                    protocol.delay(minutes=0.5)
                
                protocol.comment('--> Remove ETOH Wash')
                #===============================================
                for loop, X in enumerate(column_2_list):
                    tipcheck()
                    p1000.pick_up_tip()
                    p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                    p1000.aspirate(RemoveSup-100, rate=0.25)
                    protocol.delay(minutes=0.1)
                    p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                    p1000.aspirate(100, rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].top(z=-2))
                    p1000.default_speed = 200
                    p1000.touch_tip(speed=100)
                    p1000.dispense(200, Liquid_trash.top(z=-3))
                    protocol.delay(minutes=0.1)
                    p1000.blow_out()
                    p1000.default_speed = 100
                    p1000.move_to(Liquid_trash.top().move(types.Point(x=4,z=-3)))
                    p1000.move_to(Liquid_trash.top().move(types.Point(x=-4,z=-3)))
                    p1000.default_speed = 400
                    p1000.move_to(Liquid_trash.top(z=-5))
                    p1000.move_to(Liquid_trash.top(z=0))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                #===============================================
            
            '''
            if COLUMNS == 3:
                if DRYRUN == False:
                    protocol.delay(minutes=3)

            else:
            '''
            if DRYRUN == False:
                protocol.delay(minutes=1)

            protocol.comment('--> Removing Residual Wash')
            #===============================================
            for loop, X in enumerate(column_2_list):
                tipcheck()
                p50.pick_up_tip()
                p50.move_to(sample_plate_1[X].bottom(1))
                p50.aspirate(20, rate=0.25)
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================
            
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
            RSBVol = 26
            RSBMixRPM = 2000
            AirMultiDispense = False
            RSBMixTime = 5*60 if DRYRUN == False else 0.1*60
            #===============================================
            if AirMultiDispense == True:
                tipcheck()
                p50.pick_up_tip()
                for loop, X in enumerate(column_2_list):
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].top(z=3))
                    p50.dispense(RSBVol, rate=2)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top(z=3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            else:
                for loop, X in enumerate(column_2_list):
                    tipcheck()
                    p50.pick_up_tip()
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].bottom(z=1))
                    p50.dispense(RSBVol, rate=1)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top())
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
            #===============================================
            heatershaker.set_and_wait_for_shake_speed(rpm=RSBMixRPM)
            protocol.delay(RSBMixTime)
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
                protocol.delay(minutes=3)

            '''
            if COLUMNS == 3:
                protocol.comment('--> Adding Primer and Transferring Supernatant')
                PrimerVol    = 1.5
                PrimerMixRep = 3
                PrimerMixVol = 10
                TransferSup = 23.5
                #===============================================
                for loop, X in enumerate(column_3_list):
                    tipcheck()
                    p50.pick_up_tip()
                    protocol.comment('--> Adding Primer')
                    p50.aspirate(PrimerVol, Primer.bottom(z=1), rate=0.25)
                    protocol.comment('--> Transferring Supernatant')
                    p50.move_to(sample_plate_1[column_2_list[loop]].bottom(z=0.5))
                    p50.aspirate(TransferSup+1, rate=0.25)
                    p50.dispense(TransferSup+5, sample_plate_1[column_3_list[loop]].bottom(z=1))
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
                #===============================================
            else:
            '''
            protocol.comment('--> Transferring Supernatant')
            TransferSup = 23.5
            #===============================================
            for loop, X in enumerate(column_2_list):
                tipcheck()
                p50.pick_up_tip()
                p50.move_to(sample_plate_1[X].bottom(z=0.4))
                p50.aspirate(TransferSup/2, rate=0.25)
                protocol.delay(seconds=0.2)
                p50.move_to(sample_plate_1[X].bottom(z=0.4))
                p50.aspirate(TransferSup/2, rate=0.25)
                p50.dispense(TransferSup, sample_plate_1[column_3_list[loop]].bottom(z=1)) #Changed TransferSup+3 to TransferSup
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================

            #============================================================================================
            # GRIPPER MOVE PLATE FROM MAG PLATE TO THERMOCYCLER
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

            if COLUMNS == 3:
                if DRYRUN == False:
                    protocol.delay(minutes=0.1)
            else:
                if DRYRUN == False:
                    protocol.delay(minutes=0.1)

                protocol.comment('--> Adding Primer')
                PrimerVol    = 1.5
                PrimerMixRep = 3
                PrimerMixVol = 10
                #===============================================
                for loop, X in enumerate(column_3_list):
                    tipcheck()
                    p50.pick_up_tip()
                    p50.aspirate(PrimerVol, Primer.bottom(z=1), rate=0.25)
                    p50.dispense(PrimerVol, sample_plate_1.wells_by_name()[X].bottom(z=1))
                    p50.mix(PrimerMixRep,PrimerMixVol)
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
                #===============================================

            protocol.comment('--> Adding PCR')
            PCRVol = 25
            PCRMixRep = 10
            PCRMixVol = 50
            #===============================================
            for loop, X in enumerate(column_3_list):
                tipcheck()                
                p1000.pick_up_tip()
                p1000.mix(2,PCRVol, PCR.bottom(z=1), rate=0.5)
                p1000.aspirate(PCRVol, PCR.bottom(z=1), rate=0.25)
                p1000.dispense(PCRVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                p1000.mix(PCRMixRep, PCRMixVol, rate=0.5)
                p1000.move_to(sample_plate_1[X].bottom(z=1))
                protocol.delay(minutes=0.1)
                p1000.blow_out(sample_plate_1[X].top(z=-5))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================

        if STEP_PCRDECK == 1:
            ############################################################################################################################################
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
            thermocycler.open_lid()
            ############################################################################################################################################

        if STEP_CLEANUP_3 == 1:
            protocol.comment('==============================================')
            protocol.comment('--> Cleanup 3')
            protocol.comment('==============================================')
        
            Liquid_trash = Liquid_trash_well_3

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM THERMOCYCLER TO HEATER SHAKER
            heatershaker.open_labware_latch()    
            protocol.move_labware(
                labware=sample_plate_1,
                new_location=hs_adapter,
                use_gripper=USE_GRIPPER,
            )
            heatershaker.close_labware_latch()    
            #============================================================================================

            protocol.comment('--> ADDING AMPure (0.8x)')
            AMPureVol = 50
            SampleVol = 50
            AMPureMixRPM = 1800
            AMPureMixTime = 5*60 if DRYRUN == False else 0.1*60 # Seconds
            AMPurePremix = 3 if DRYRUN == False else 1
            #===============================================
            if AMP_3_AirMultiDis == True:
                tipcheck()
                p1000.pick_up_tip()
                p1000.mix(AMPurePremix,40, AMPure.bottom(z=1))
                for loop, X in enumerate(column_3_list):
                    p1000.aspirate(AMPureVol, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(AMPureVol, sample_plate_1[X].top(z=1), rate=1)
                    protocol.delay(seconds=0.2)
                    p1000.blow_out(sample_plate_1[X].top(z=-1))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            else:
                for loop, X in enumerate(column_3_list):
                    tipcheck()
                    p1000.pick_up_tip()
                    p1000.mix(AMPurePremix,AMPureVol+3, AMPure.bottom(z=1))
                    p1000.aspirate(AMPureVol+3, AMPure.bottom(z=1), rate=0.25)
                    p1000.dispense(3, AMPure.bottom(z=1), rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(AMPure.top(z=-3))
                    p1000.default_speed = 100
                    p1000.move_to(AMPure.top().move(types.Point(x=4,z=-3)))
                    p1000.move_to(AMPure.top().move(types.Point(x=-4,z=-3)))
                    p1000.default_speed = 400
                    p1000.dispense(AMPureVol, sample_plate_1[X].bottom(z=1), rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].bottom(z=5))
                    for Mix in range(2):
                        p1000.aspirate(50, rate=0.5)
                        p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                        p1000.aspirate(20, rate=0.5)
                        p1000.dispense(20, rate=0.5)
                        p1000.move_to(sample_plate_1[X].bottom(z=3))
                        p1000.dispense(50,rate=0.5)
                        Mix += 1
                    p1000.move_to(sample_plate_1[X].top(z=-3))
                    protocol.delay(seconds=0.2)
                    p1000.blow_out(sample_plate_1[X].top(z=-3))
                    p1000.touch_tip(speed=100)
                    p1000.default_speed = 400
                    p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.move_to(sample_plate_1[X].top(z=0))
                    p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
            #===============================================
            heatershaker.set_and_wait_for_shake_speed(rpm=AMPureMixRPM)
            protocol.delay(AMPureMixTime)
            heatershaker.deactivate_shaker()        

            #============================================================================================
            # GRIPPER MOVE sample_plate_1 FROM HEATERSHAKER TO MAGPLATE
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
            #===============================================
            for loop, X in enumerate(column_3_list):
                tipcheck()
                p1000.pick_up_tip()
                p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                p1000.aspirate(RemoveSup-100, rate=0.25)
                protocol.delay(minutes=0.1)
                p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                p1000.aspirate(100, rate=0.25)
                p1000.default_speed = 5
                p1000.move_to(sample_plate_1[X].top(z=-2))
                p1000.default_speed = 200
                p1000.touch_tip(speed=100)
                p1000.dispense(200, Liquid_trash.top(z=-3))
                protocol.delay(minutes=0.1)
                p1000.blow_out()
                p1000.default_speed = 100
                p1000.move_to(Liquid_trash.top().move(types.Point(x=4,z=-3)))
                p1000.move_to(Liquid_trash.top().move(types.Point(x=-4,z=-3)))
                p1000.default_speed = 400
                p1000.move_to(Liquid_trash.top(z=-5))
                p1000.move_to(Liquid_trash.top(z=0))
                p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                p200_tips += 1
            #===============================================
    
            for X in range(2):
                protocol.comment('--> ETOH Wash')
                ETOHMaxVol = 150
                #===============================================
                if ETOH_3_AirMultiDis == True:
                    tipcheck()
                    p1000.pick_up_tip()
                    for loop, X in enumerate(column_3_list):
                        p1000.aspirate(ETOHMaxVol, EtOH_3.bottom(z=1))
                        p1000.move_to(EtOH_3.top(z=0))
                        p1000.move_to(EtOH_3.top(z=-5))
                        p1000.default_speed = 100
                        p1000.move_to(EtOH_3.top().move(types.Point(x=4,z=-3)))
                        p1000.move_to(EtOH_3.top().move(types.Point(x=-4,z=-3)))
                        p1000.default_speed = 400
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out(sample_plate_1[X].top(z=-2))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                else:
                    for loop, X in enumerate(column_3_list):
                        tipcheck()
                        p1000.pick_up_tip()
                        p1000.aspirate(ETOHMaxVol, EtOH_3.bottom(z=1))
                        p1000.move_to(EtOH_3.top(z=0))
                        p1000.move_to(EtOH_3.top(z=-5))
                        p1000.default_speed = 100
                        p1000.move_to(EtOH_3.top().move(types.Point(x=4,z=-3)))
                        p1000.move_to(EtOH_3.top().move(types.Point(x=-4,z=-3)))
                        p1000.default_speed = 400
                        p1000.move_to(sample_plate_1[X].top(z=-2))
                        p1000.dispense(ETOHMaxVol, rate=1)
                        protocol.delay(minutes=0.1)
                        p1000.blow_out()
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.move_to(sample_plate_1[X].top(z=0))
                        p1000.move_to(sample_plate_1[X].top(z=5))
                        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                        p200_tips += 1
                #===============================================
                if DRYRUN == False:
                    protocol.delay(minutes=0.5)
                
                protocol.comment('--> Remove ETOH Wash')
                #===============================================
                for loop, X in enumerate(column_3_list):
                    tipcheck()
                    p1000.pick_up_tip()
                    p1000.move_to(sample_plate_1[X].bottom(z=3.5))
                    p1000.aspirate(RemoveSup-100, rate=0.25)
                    protocol.delay(minutes=0.1)
                    p1000.move_to(sample_plate_1[X].bottom(z=0.75))
                    p1000.aspirate(100, rate=0.25)
                    p1000.default_speed = 5
                    p1000.move_to(sample_plate_1[X].top(z=-2))
                    p1000.default_speed = 200
                    p1000.touch_tip(speed=100)
                    p1000.dispense(200, Liquid_trash.top(z=-3))
                    protocol.delay(minutes=0.1)
                    p1000.blow_out()
                    p1000.default_speed = 100
                    p1000.move_to(Liquid_trash.top().move(types.Point(x=4,z=-3)))
                    p1000.move_to(Liquid_trash.top().move(types.Point(x=-4,z=-3)))
                    p1000.default_speed = 400
                    p1000.move_to(Liquid_trash.top(z=-5))
                    p1000.move_to(Liquid_trash.top(z=0))
                    p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
                    p200_tips += 1
                #===============================================
            
            if COLUMNS == 3:
                if DRYRUN == False:
                    protocol.delay(minutes=3)

            else:
                if DRYRUN == False:
                    protocol.delay(minutes=2)

                protocol.comment('--> Removing Residual Wash')
                #===============================================
                for loop, X in enumerate(column_3_list):
                    tipcheck()
                    p50.pick_up_tip()
                    p50.move_to(sample_plate_1[X].bottom(1))
                    p50.aspirate(20, rate=0.25)
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
                #===============================================

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
            RSBVol = 26
            RSBMixRPM = 2000
            RSBMixTime = 2*60 if DRYRUN == False else 0.1*60
            #===============================================
            if RSB_3_AirMultiDis == True:
                tipcheck()
                p50.pick_up_tip()
                for loop, X in enumerate(column_3_list):
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].top(z=3))
                    p50.dispense(RSBVol, rate=2)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top(z=3))
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            else:
                for loop, X in enumerate(column_3_list):
                    tipcheck()
                    p50.pick_up_tip()
                    p50.aspirate(RSBVol, RSB.bottom(z=1))
                    p50.move_to(sample_plate_1.wells_by_name()[X].bottom(z=1))
                    p50.dispense(RSBVol, rate=1)
                    p50.blow_out(sample_plate_1.wells_by_name()[X].top())
                    p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                    p50_tips += 1
            #===============================================
            heatershaker.set_and_wait_for_shake_speed(rpm=RSBMixRPM)
            protocol.delay(RSBMixTime)
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
                protocol.delay(minutes=3)

            protocol.comment('--> Transferring Supernatant')
            TransferSup = 23.5
            #===============================================
            for loop, X in enumerate(column_3_list):
                tipcheck()
                p50.pick_up_tip()
                p50.move_to(sample_plate_1[X].bottom(z=0.4))
                p50.aspirate(TransferSup/2, rate=0.25)
                protocol.delay(seconds=0.2)
                p50.move_to(sample_plate_1[X].bottom(z=0.4))
                p50.aspirate(TransferSup/2, rate=0.25)
                p50.dispense(TransferSup, sample_plate_1[column_4_list[loop]].bottom(z=1)) #Changed TransferSup+3 to TransferSup
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
            #===============================================

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
            # Resetting FX
            p1000.aspirate(COLUMNS*15, Liquid_trash_well_1.bottom(z=1))
            p1000.dispense(COLUMNS*15, FX.bottom(z=1))
            # Resetting LIG
            p1000.aspirate(COLUMNS*45, Liquid_trash_well_1.bottom(z=1))
            p1000.dispense(COLUMNS*45, LIG.bottom(z=1))
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

                p1000.aspirate(150, Liquid_trash_well_3.bottom(z=1))
                p1000.dispense(150, EtOH_3.bottom(z=1))
                p1000.aspirate(150, Liquid_trash_well_3.bottom(z=1))
                p1000.dispense(150, EtOH_3.bottom(z=1))
            # Resetting AMPURE
            for X in range(COLUMNS):
                p1000.aspirate(COLUMNS*65, Liquid_trash_well_1.bottom(z=1))
                p1000.dispense(COLUMNS*65, AMPure.bottom(z=1))
            for X in range(COLUMNS):
                p1000.aspirate(COLUMNS*50, Liquid_trash_well_2.bottom(z=1))
                p1000.dispense(COLUMNS*50, AMPure.bottom(z=1))
            for X in range(COLUMNS):
                p1000.aspirate(COLUMNS*50, Liquid_trash_well_3.bottom(z=1))
                p1000.dispense(COLUMNS*50, AMPure.bottom(z=1))
            # Resetting PCR
            p1000.aspirate(COLUMNS*25, Liquid_trash_well_3.bottom(z=1))
            p1000.dispense(COLUMNS*25, PCR.bottom(z=1))
            # Resetting RSB
            p1000.aspirate(COLUMNS*50, Liquid_trash_well_2.bottom(z=1))
            p1000.dispense(COLUMNS*50, RSB.bottom(z=1))
            p1000.aspirate(COLUMNS*26, Liquid_trash_well_3.bottom(z=1))
            p1000.dispense(COLUMNS*26, RSB.bottom(z=1))
            p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
            p200_tips += 1
            tipcheck()

            p50.pick_up_tip()
            # Removing Final Samples
            for loop, X in enumerate(column_3_list):
                p50.aspirate(23.5, sample_plate_1[X].bottom(z=1))
                p50.dispense(23.5, Liquid_trash_well_3.bottom(z=1))
            # Resetting Initial Samples
            for loop, X in enumerate(column_1_list):
                p50.aspirate(19.5, Liquid_trash_well_1.bottom(z=1))
                p50.dispense(19.5, sample_plate_1[X].bottom(z=1))
            # Resetting Barcodes
            for loop, X in enumerate(barcodes):
                p50.aspirate(5, Liquid_trash_well_1.bottom(z=1))
                p50.dispense(5, sample_plate_1[X].bottom(z=1))
            # Resetting PRIMER
            p50.aspirate(COLUMNS*1.5, Liquid_trash_well_3.bottom(z=1))
            p50.dispense(COLUMNS*1.5, Primer.bottom(z=1))
            p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
            p50_tips += 1
            tipcheck()

        protocol.comment('Number of Resets: '+str(Resetcount))