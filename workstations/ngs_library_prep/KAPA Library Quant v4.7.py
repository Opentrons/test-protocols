from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'KAPA Library Quant v4.7',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}

# SCRIPT SETTINGS
DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack

# PROTOCOL SETTINGS
COLUMNS     = 10             # 8x, 16x, or 24x   
FORMAT      = '384'         # 96 or 384
INICOLUMN1  = 'A1'
INICOLUMN2  = 'A2'
INICOLUMN3  = 'A3'
INICOLUMN4  = 'A4'
INICOLUMN5  = 'A5'
INICOLUMN6  = 'A6'
INICOLUMN7  = 'A7'
INICOLUMN8  = 'A8'
INICOLUMN9  = 'A9'
INICOLUMN10  = 'A10'

# PROTOCOL BLOCKS
STEP_DILUTE         = 1
STEP_MIX            = 1
STEP_DISPENSE       = 1

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

p200_tips           = 0
p50_tips            = 0
qPCRStockVol        = 0
Resetcount          = 0

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
    global qPCRStockVol
    global Resetcount

    protocol.comment('THIS IS A DRY RUN') if DRYRUN == True else protocol.comment('THIS IS A REACTION RUN')
    protocol.comment('USED TIPS WILL GO IN TRASH') if TIP_TRASH == True else protocol.comment('USED TIPS WILL BE RE-RACKED')

    # DECK SETUP AND LABWARE
    # ========== FIRST ROW ===========

    heatershaker        = protocol.load_module('heaterShakerModuleV1','D1')
    hs_adapter          = heatershaker.load_adapter('opentrons_96_pcr_adapter')
    dilution_plate      = hs_adapter.load_labware('nest_96_wellplate_2ml_deep') 
    if FORMAT == '96':
        qpcrplate       = protocol.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt', 'D2') 
    if FORMAT == '384':
        qpcrplate       = protocol.load_labware('appliedbiosystemsmicroamp_384_wellplate_40ul', 'D2') 
    temp_block          = protocol.load_module('temperature module gen2', 'D3')
    temp_adapter        = temp_block.load_adapter('opentrons_96_well_aluminum_block')
    mix_plate           = temp_adapter.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    # ========== SECOND ROW ==========
    mag_block           = protocol.load_module('magneticBlockV1', 'C1')
    source_plate        = mag_block.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt') 
    tiprack_50_1        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'C2')
    tiprack_50_2        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'C3')
    # ========== THIRD ROW ===========
    thermocycler    = protocol.load_module('thermocycler module gen2')
    reagent_thermo  = thermocycler.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt')
    tiprack_50_3        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'B2')
    tiprack_200_1       = protocol.load_labware('opentrons_flex_96_tiprack_200ul', 'B3')
    # ========== FOURTH ROW ==========
    tiprack_50_4        = protocol.load_labware('opentrons_flex_96_tiprack_50ul', 'A2')

    # REAGENT PLATE
    STD                 = reagent_thermo['A1']
    qPCR_1              = reagent_thermo['A3']
    qPCR_2              = reagent_thermo['A4']
    qPCR_3              = reagent_thermo['A5']
    qPCR_4              = reagent_thermo['A6']
    H20                 = reagent_thermo['A8']

    # RESERVOIR

    #pipette
    p1000 = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_200_1])
    p50 = protocol.load_instrument("flex_8channel_50", "right", tip_racks=[tiprack_50_1,tiprack_50_2,tiprack_50_3,tiprack_50_4])
    p200_tipracks = 1
    p50_tipracks = 4
    # samples

    #tip and sample tracking
    column_1_list = [INICOLUMN1,INICOLUMN2,INICOLUMN3,INICOLUMN4,INICOLUMN5,INICOLUMN6,INICOLUMN7,INICOLUMN8,INICOLUMN9,INICOLUMN10]
    column_2_list = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10']
    column_3_list = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10']
    column_4_list = ['A2','A3','A4','A5','A6','A7','A8','A9','A10','A11']
    column_5_list = [['A1','A2','B1','B2'],['A3','A4','B3','B4'],['A5','A6','B5','B6'],['A7','A8','B7','B8'],['A9','A10','B9','B10'],
    ['A11','A12','B11','B12'],['A13','A14','B13','B14'],['A15','A16','B15','B16'],['A17','A18','B17','B18'],['A19','A20','B19','B20'],['A21','A22','B21','B22']]

    def AspqPCRStockVol(Vol):
        global qPCRStockVol
        qPCRStockVol += int(Vol)
        if int(qPCRStockVol) <120:
            qPCR = qPCR_1
        if int(qPCRStockVol) >=120:
            qPCR = qPCR_2
        if int(qPCRStockVol) >=240:
            qPCR = qPCR_3
        if int(qPCRStockVol) >=360:
            qPCR = qPCR_4

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
    thermocycler.open_lid()
    heatershaker.open_labware_latch()
    protocol.pause("Ready")
    heatershaker.close_labware_latch()

    if STEP_DILUTE == 1:
        protocol.comment('==============================================')
        protocol.comment('--> Diluting Sample')
        protocol.comment('==============================================')
        protocol.comment('--> Adding Sample to Diluent')
        SampleVol    = 2
        DilMixRPM = 1600
        DilMixTime = 2*60 if DRYRUN == False else 0.1*60
        #===============================================
        for loop, X in enumerate(column_1_list):
            tipcheck()
            p50.pick_up_tip()
            p50.mix(2,SampleVol+3, source_plate.wells_by_name()[X].bottom(z=1))
            p50.aspirate(SampleVol+3, source_plate.wells_by_name()[X].bottom(z=1))
            p50.dispense(3, source_plate.wells_by_name()[X].bottom(z=1))
            p50.dispense(SampleVol+1, dilution_plate.wells_by_name()[column_2_list[loop]].bottom(z=14))
            p50.aspirate(10, dilution_plate.wells_by_name()[column_2_list[loop]].bottom(z=10))
            p50.dispense(10, dilution_plate.wells_by_name()[column_2_list[loop]].bottom(z=10))
            p50.blow_out(dilution_plate.wells_by_name()[column_2_list[loop]].bottom(z=19.5))
            p50.move_to(dilution_plate.wells_by_name()[column_2_list[loop]].bottom(z=16))
            p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
            p50_tips += 1
            if loop == COLUMNS-1:
                break
        #===============================================
        heatershaker.set_and_wait_for_shake_speed(rpm=DilMixRPM)
        protocol.delay(DilMixTime)
        heatershaker.deactivate_shaker()

    if STEP_MIX == 1:
        protocol.comment('==============================================')
        protocol.comment('--> Adding qPCR Mix')
        protocol.comment('==============================================')
        protocol.comment('--> Adding H20')
        p1000.pick_up_tip()
        p1000.aspirate((10+(15*COLUMNS)+10), H20.bottom(z=1),rate=0.5)
        p1000.dispense(10, mix_plate.wells_by_name()['A1'].bottom(z=1),rate=0.5)
        #===============================================
        for loop, X in enumerate(column_4_list):
            p1000.dispense(15, mix_plate.wells_by_name()[X].bottom(z=1),rate=0.5)
            if loop == COLUMNS-1:
                break
        #===============================================
        p1000.return_tip() if TIP_TRASH == False else p1000.drop_tip()
        p200_tips += 1

        protocol.comment('--> Adding qPCR')        
        qPCRVol = 30
        #===============================================
        for loop, X in enumerate(column_3_list):
            tipcheck()
            p50.pick_up_tip()
            qPCRStockVol += 30
            if int(qPCRStockVol) <120:
                qPCR = qPCR_1
            if int(qPCRStockVol) >=120:
                qPCR = qPCR_2
            if int(qPCRStockVol) >=240:
                qPCR = qPCR_3
            if int(qPCRStockVol) >=360:
                qPCR = qPCR_4            
            protocol.comment('--> qPCRStockVol: '+str(qPCRStockVol))
            p50.mix(2,qPCRVol, qPCR.bottom(z=1),rate=0.5)
            p50.aspirate(qPCRVol, qPCR.bottom(z=1),rate=0.5)
            p50.dispense(qPCRVol, mix_plate.wells_by_name()[X].bottom(z=1),rate=0.5)
            p50.aspirate(qPCRVol, mix_plate.wells_by_name()[X].bottom(z=1),rate=0.5)
            p50.dispense(qPCRVol, mix_plate.wells_by_name()[X].bottom(z=1),rate=0.5)
            p50.default_speed = 10
            p50.move_to(mix_plate.wells_by_name()[X].top(z=11))
            p50.default_speed = 400
            p50.blow_out()
            p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
            p50_tips += 1
            if loop == (COLUMNS+1)-1:
                break
        #===============================================

        protocol.comment('==============================================')
        protocol.comment('--> Adding Standards to Mix')
        protocol.comment('==============================================')
        SampleVol = 10
        p50.pick_up_tip()
        p50.aspirate(SampleVol, STD.bottom(z=0.6), rate=0.5)
        p50.dispense(SampleVol, mix_plate['A1'].bottom(z=1), rate=0.5)
        p50.aspirate(SampleVol, mix_plate['A1'].bottom(z=1), rate=0.5)
        p50.dispense(SampleVol, mix_plate['A1'].bottom(z=1), rate=0.5)
        p50.default_speed = 2.5
        p50.move_to(mix_plate['A1'].top(z=-1))
        protocol.delay(seconds=2)
        p50.blow_out(mix_plate['A1'].top(z=-1))
        p50.default_speed = 400
        p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()

        protocol.comment('==============================================')
        protocol.comment('--> Adding Diluted Sample to Mix')
        protocol.comment('==============================================')
        SampleVol = 5
        #===============================================
        for loop, X in enumerate(column_2_list):
            tipcheck()
            p50.pick_up_tip()
            p50.aspirate(SampleVol, dilution_plate.wells_by_name()[X].bottom(z=16))
            p50.dispense(SampleVol, mix_plate.wells_by_name()[column_4_list[loop]].bottom(z=1),rate=0.5)
            p50.aspirate(SampleVol, mix_plate.wells_by_name()[column_4_list[loop]].bottom(z=1),rate=0.5)
            p50.dispense(SampleVol, mix_plate.wells_by_name()[column_4_list[loop]].bottom(z=1),rate=0.5)
            p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
            p50_tips += 1
            if loop == (COLUMNS+1)-1:
                break
        #===============================================

    if STEP_DISPENSE == 1:
        '''
        if FORMAT == '96':
        '''
        if FORMAT == '384':
            protocol.comment('==============================================')
            protocol.comment('--> Dispensing 384 well')
            protocol.comment('==============================================')
            qPCRVol = 40
            Multidispense = [10.1,10.2,9.8,9.9]
            #===============================================
            for loop, X in enumerate(column_3_list):
                tipcheck()
                p50.pick_up_tip()
                p50.mix(5,qPCRVol-5, mix_plate[X].bottom(z=1),rate=0.5)
                p50.aspirate(qPCRVol+5, mix_plate[X].bottom(z=0.6), rate=0.25)
                p50.dispense(2, mix_plate[X].bottom(z=0.6), rate=0.25)
                protocol.delay(seconds=0.2)
                #===============================================
                for loop2, X in enumerate(column_5_list[loop]):
                    p50.move_to(qpcrplate[X].top(z=1.0))
                    protocol.delay(seconds=0.2)
                    p50.default_speed = 10
                    p50.move_to(qpcrplate[X].center())
                    p50.default_speed = 2.5
                    p50.dispense(Multidispense[loop2], qpcrplate[X].bottom(z=1), rate=0.25)
                    protocol.delay(seconds=0.2)
                    p50.default_speed = 100
                #===============================================
                p50.default_speed = 400
                p50.return_tip() if TIP_TRASH == False else p50.drop_tip()
                p50_tips += 1
                if loop == (COLUMNS+1)-1:
                    break
            #===============================================