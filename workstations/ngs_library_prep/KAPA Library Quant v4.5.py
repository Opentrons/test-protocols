from opentrons import protocol_api
from opentrons import types

metadata = {
    'protoclName': 'KAPA Library Quant v4.5',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.15'
    }

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.15",
}

# SCRIPT SETTINGS
DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
NGSHS       = 'YES'         # YES or NO, Sets whether there is the Magnetic Block on the Deck (for post-NGS Setup)
NGSTHERMO   = 'YES'         # YES or NO, Sets whether there is the Thermoycler on the Deck (for post-NGS Setup)
NGSTEMP     = 'YES'         # YES or NO, Sets whether there is the Temp Block on the Deck (for post-NGS Setup)
TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack

# PROTOCOL SETTINGS
SAMPLES     = '24x'         # 8x, 16x, or 24x   
FORMAT      = '384'         # 96 or 384
INICOLUMN1  = 'A1'
INICOLUMN2  = 'A3'
INICOLUMN3  = 'A5'
MODULESONDECK       = True

# PROTOCOL BLOCKS
STEP_DILUTE         = 1
STEP_MIX            = 1
STEP_DISPENSE       = 1

############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

p500_tips           = 0
p50_tips            = 0
WasteVol            = 0
Resetcount          = 0

ABR_TEST            = False
if ABR_TEST == True:
    DRYRUN          = True           # Overrides to only DRYRUN
    TIP_TRASH       = False          # Overrides to only REUSING TIPS
    RUN             = 3              # Repetitions
else:
    RUN             = 1

def run(protocol: protocol_api.ProtocolContext):

    global p500_tips
    global p50_tips
    global WasteVol
    global Resetcount

    protocol.comment('THIS IS A DRY RUN') if DRYRUN == True else protocol.comment('THIS IS A REACTION RUN')
    protocol.comment('USED TIPS WILL GO IN TRASH') if TIP_TRASH == True else protocol.comment('USED TIPS WILL BE RE-RACKED')

    # DECK SETUP AND LABWARE
    # ========== FIRST ROW ===========
    if MODULESONDECK == False:
        protocol.comment("THIS IS A NO MODULE RUN")
        source_plate       = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '1') 
        reservoir           = protocol.load_labware('nest_12_reservoir_15ml','2')
        dilution_plate   = protocol.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul', '3')
    # ========== SECOND ROW ==========
        tiprack_50_1        = protocol.load_labware('opentrons_ot3_96_tiprack_50ul', '5')
        tiprack_50_2        = protocol.load_labware('opentrons_ot3_96_tiprack_50ul', '6')
    # ========== THIRD ROW ===========
        reagent_thermo      = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt','7') #<--- NEST Strip Tubes
        tiprack_200_1       = protocol.load_labware('opentrons_ot3_96_tiprack_200ul', '8')
        if FORMAT == '96':
            qpcrplate           = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '9') 
        if FORMAT == '384':
            qpcrplate           = protocol.load_labware('corning_384_wellplate_112ul_flat', '9') 
    # ========== FOURTH ROW ==========

    if MODULESONDECK == True:
        protocol.comment("THIS IS A MODULE RUN")
    # ========== FIRST ROW ===========
        if NGSHS == 'YES':
            heatershaker        = protocol.load_module('heaterShakerModuleV1','1')
            source_plate        = heatershaker.load_labware('nest_96_wellplate_100ul_pcr_full_skirt') 
        else:
            source_plate        = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt','1') 
        reservoir           = protocol.load_labware('nest_12_reservoir_15ml','2')
        if NGSTEMP == 'YES':
            temp_block       = protocol.load_module('temperature module gen2', '3')
            dilution_plate   = temp_block.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul')
        else:
            dilution_plate         = protocol.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul','3')
    # ========== SECOND ROW ==========
        tiprack_50_1        = protocol.load_labware('opentrons_ot3_96_tiprack_50ul', '5')
        tiprack_50_2        = protocol.load_labware('opentrons_ot3_96_tiprack_50ul', '6')
    # ========== THIRD ROW ===========
        if NGSTHERMO == 'YES':
            thermocycler        = protocol.load_module('thermocycler module gen2')
            reagent_thermo      = thermocycler.load_labware('nest_96_wellplate_100ul_pcr_full_skirt') #<--- NEST Strip Tubes
        else:
            reagent_thermo      = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt','7') #<--- NEST Strip Tubes
        tiprack_200_1       = protocol.load_labware('opentrons_ot3_96_tiprack_200ul', '8')
        if FORMAT == '96':
            qpcrplate           = protocol.load_labware('nest_96_wellplate_100ul_pcr_full_skirt', '9') 
        if FORMAT == '384':
            qpcrplate           = protocol.load_labware('corning_384_wellplate_112ul_flat', '9') 
    # ========== FOURTH ROW ==========

    # REAGENT PLATE
    STD         = reagent_thermo['A1']
    PCR         = reagent_thermo['A3']

    # RESERVOIR
    DIL         = reservoir['A5']

    #pipette
    p1000 = protocol.load_instrument("p1000_multi_gen3", "left", tip_racks=[tiprack_200_1])
    p50 = protocol.load_instrument("p50_multi_gen3", "right", tip_racks=[tiprack_50_1,tiprack_50_2])
    
   # samples

    #tip and sample tracking
    if SAMPLES == '8x':
        protocol.comment("There are 8 Samples")
        samplecolumns    = 1
    elif SAMPLES == '16x':
        protocol.comment("There are 16 Samples")
        samplecolumns    = 2
    elif SAMPLES == '24x':
        protocol.comment("There are 24 Samples")
        samplecolumns    = 3
    else:
        protocol.pause("ERROR?")
    
############################################################################################################################################
############################################################################################################################################
############################################################################################################################################

    # commands
    if MODULESONDECK == True:
        thermocycler.open_lid()
        heatershaker.open_labware_latch()
        protocol.pause("Ready")
        heatershaker.close_labware_latch()

    if STEP_DILUTE == 1:
        protocol.comment('==============================================')
        protocol.comment('--> Dispensing Diluent Part 1 and Part 2')
        protocol.comment('==============================================')
        p1000.pick_up_tip()
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = 'A2'
            Y = 'A6'
            p1000.move_to(DIL.bottom(z=0.1))
            p1000.mix(3,200, rate=0.5)
            p1000.move_to(DIL.top(z=+5))
            protocol.delay(seconds=2)
            p1000.aspirate(200, DIL.bottom(z=0.1), rate=0.25)
            p1000.dispense(98, dilution_plate[X].bottom(z=0.1), rate=0.25)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.dispense(95, dilution_plate[Y].bottom(z=0.1), rate=0.25)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[Y].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.move_to(DIL.top())
            p1000.blow_out()
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = 'A3'
            Y = 'A7'
            p1000.move_to(DIL.bottom(z=0.1))
            p1000.mix(3,200, rate=0.5)
            p1000.move_to(DIL.top(z=+5))
            protocol.delay(seconds=2)
            p1000.aspirate(200, DIL.bottom(z=0.1), rate=0.25)
            p1000.dispense(98, dilution_plate[X].bottom(z=0.1), rate=0.25)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.dispense(95, dilution_plate[Y].bottom(z=0.1), rate=0.25)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[Y].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.move_to(DIL.top())
            p1000.blow_out()
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = 'A4'
            Y = 'A8'
            p1000.move_to(DIL.bottom(z=0.1))
            p1000.mix(3,200, rate=0.5)
            p1000.move_to(DIL.top(z=+5))
            protocol.delay(seconds=2)
            p1000.aspirate(200, DIL.bottom(z=0.1), rate=0.25)
            p1000.dispense(98, dilution_plate[X].bottom(z=0.1), rate=0.25)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.dispense(95, dilution_plate[Y].bottom(z=0.1), rate=0.25)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[Y].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.move_to(DIL.top())
            p1000.blow_out()
        p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
        
        protocol.comment('==============================================')
        protocol.comment('--> Adding Sample to Diluent Part 1')
        protocol.comment('==============================================')
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = INICOLUMN1
            Y = 'A2'
            p50.pick_up_tip()
            p50.aspirate(2, source_plate[X].bottom(z=0.1), rate=0.25)
            p50.dispense(2, dilution_plate[Y].center(), rate=0.5)
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = INICOLUMN2
            Y = 'A3'
            p50.pick_up_tip()
            p50.aspirate(2, source_plate[X].bottom(z=0.1), rate=0.25)
            p50.dispense(2, dilution_plate[Y].center(), rate=0.5)
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = INICOLUMN3
            Y = 'A4'
            p50.pick_up_tip()
            p50.aspirate(2, source_plate[X].bottom(z=0.1), rate=0.25)
            p50.dispense(2, dilution_plate[Y].center(), rate=0.5)
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()

        protocol.comment('--> Mixing')
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = 'A2'
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            if DRYRUN == 'NO':
                p1000.mix(50, 80)
            else:
                p1000.mix(1, 80)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = 'A3'
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            if DRYRUN == 'NO':
                p1000.mix(50, 80)
            else:
                p1000.mix(1, 80)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = 'A4'
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            if DRYRUN == 'NO':
                p1000.mix(50, 80)
            else:
                p1000.mix(1, 80)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()

        protocol.comment('==============================================')
        protocol.comment('--> Adding Diluted Sample to Diluent Part 2')
        protocol.comment('==============================================')
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = 'A2'
            Y = 'A6'
            p50.pick_up_tip()
            p50.aspirate(5, dilution_plate[X].center(), rate=0.5)
            p50.dispense(5, dilution_plate[Y].center(), rate=0.5)
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = 'A3'
            Y = 'A7'
            p50.pick_up_tip()
            p50.aspirate(5, dilution_plate[X].center(), rate=0.5)
            p50.dispense(5, dilution_plate[Y].center(), rate=0.5)
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = 'A4'
            Y = 'A8'
            p50.pick_up_tip()
            p50.aspirate(5, dilution_plate[X].center(), rate=0.5)
            p50.dispense(5, dilution_plate[Y].center(), rate=0.5)
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()

        protocol.comment('--> Mixing')
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = 'A6'
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            if DRYRUN == 'NO':
                p1000.mix(50, 80)
            else:
                p1000.mix(1, 80)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = 'A7'
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            if DRYRUN == 'NO':
                p1000.mix(50, 80)
            else:
                p1000.mix(1, 80)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = 'A8'
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            if DRYRUN == 'NO':
                p1000.mix(50, 80)
            else:
                p1000.mix(1, 80)
            p1000.default_speed = 5
            p1000.move_to(dilution_plate[X].top())
            protocol.delay(seconds=2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()

    if STEP_MIX == 1:
        protocol.comment('==============================================')
        protocol.comment('--> Adding qPCR Mix')
        protocol.comment('==============================================')
        qPCRVol = 50
        p1000.pick_up_tip()
        p1000.aspirate((qPCRVol), PCR.bottom(z=0.1), rate=0.25)
        p1000.dispense(qPCRVol, dilution_plate['A9'].bottom(z=0.1), rate=0.25)
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = 'A10'
            p1000.aspirate((qPCRVol), PCR.bottom(z=0.1), rate=0.25)
            p1000.dispense(qPCRVol, dilution_plate[X].bottom(z=0.1), rate=0.25)
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = 'A11'
            p1000.aspirate((qPCRVol), PCR.bottom(z=0.1), rate=0.25)
            p1000.dispense(qPCRVol, dilution_plate[X].bottom(z=0.1), rate=0.25)
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = 'A12'
            p1000.aspirate((qPCRVol), PCR.bottom(z=0.1), rate=0.25)
            p1000.dispense(qPCRVol, dilution_plate[X].bottom(z=0.1), rate=0.25)
        p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()

        protocol.comment('==============================================')
        protocol.comment('--> Adding Standards to Mix')
        protocol.comment('==============================================')
        SampleVol = 12.5
        p50.pick_up_tip()
        p50.aspirate(SampleVol, STD.bottom(z=0.1), rate=0.5)
        p50.dispense(SampleVol, dilution_plate['A9'].bottom(z=0.1), rate=0.5)
        p50.default_speed = 2.5
        p50.move_to(dilution_plate['A9'].center())
        protocol.delay(seconds=2)
        p50.default_speed = 400
        p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()

        protocol.comment('==============================================')
        protocol.comment('--> Adding Diluted Sample to Mix')
        protocol.comment('==============================================')
        if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
            X = 'A6'
            Y = 'A10'
            p50.pick_up_tip()
            p50.aspirate(SampleVol, dilution_plate[X].center(), rate=0.5)
            p50.dispense(SampleVol, dilution_plate[Y].bottom(z=0.1), rate=0.5)
            p50.default_speed = 2.5
            p50.move_to(dilution_plate[Y].center())
            protocol.delay(seconds=2)
            p50.default_speed = 400
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()
        if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
            X = 'A7'
            Y = 'A11'
            p50.pick_up_tip()
            p50.aspirate(SampleVol, dilution_plate[X].center(), rate=0.5)
            p50.dispense(SampleVol, dilution_plate[Y].bottom(z=0.1), rate=0.5)
            p50.default_speed = 2.5
            p50.move_to(dilution_plate[Y].center())
            protocol.delay(seconds=2)
            p50.default_speed = 400
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()
        if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
            X = 'A8'
            Y = 'A12'
            p50.pick_up_tip()
            p50.aspirate(SampleVol, dilution_plate[X].center(), rate=0.5)
            p50.dispense(SampleVol, dilution_plate[Y].bottom(z=0.1), rate=0.5)
            p50.default_speed = 2.5
            p50.move_to(dilution_plate[Y].center())
            protocol.delay(seconds=2)
            p50.default_speed = 400
            p50.drop_tip() if DRYRUN == 'NO' else p50.return_tip()

    if STEP_DISPENSE == 1:
        if FORMAT == '96':
            protocol.comment('==============================================')
            protocol.comment('--> Dispensing 96 well')
            protocol.comment('==============================================')
            X = 'A9'
            Y1 = 'A1'
            Y2 = 'A2'
            Y3 = 'A3' 
            p1000.pick_up_tip()
            p1000.aspirate(60, dilution_plate[X].bottom(z=0.1), rate=0.5)
            p1000.dispense(20, qpcrplate[Y1].bottom(z=0.1), rate=0.5)
            p1000.dispense(20, qpcrplate[Y2].bottom(z=0.1), rate=0.5)
            p1000.dispense(20, qpcrplate[Y3].bottom(z=0.1), rate=0.5)
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
            if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
                X = 'A10'
                Y1 = 'A4'
                Y2 = 'A5'
                Y3 = 'A6' 
                p1000.pick_up_tip()
                p1000.aspirate(60, dilution_plate[X].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y1].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y2].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y3].bottom(z=0.1), rate=0.5)
                p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
            if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
                X = 'A11'
                Y1 = 'A7'
                Y2 = 'A8'
                Y3 = 'A9'
                p1000.pick_up_tip()
                p1000.aspirate(60, dilution_plate[X].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y1].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y2].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y3].bottom(z=0.1), rate=0.5)
                p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
            if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
                X = 'A12'
                Y1 = 'A10'
                Y2 = 'A11'
                Y3 = 'A12'
                p1000.pick_up_tip()
                p1000.aspirate(60, dilution_plate[X].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y1].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y2].bottom(z=0.1), rate=0.5)
                p1000.dispense(20, qpcrplate[Y3].bottom(z=0.1), rate=0.5)
                p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip() 
        if FORMAT == '384':
            protocol.comment('==============================================')
            protocol.comment('--> Dispensing 384 well')
            protocol.comment('==============================================')
            X = 'A9'
            Y1 = 'A1'
            Y2 = 'A2'
            Y3 = 'A3' 
            p1000.pick_up_tip()
            p1000.move_to(dilution_plate[X].bottom(z=0.1))
            p1000.mix(30,58)
            p1000.aspirate(62, dilution_plate[X].bottom(z=0.1), rate=0.25)
            protocol.delay(seconds=0.2)
            p1000.move_to(qpcrplate[Y1].top(z=1.0))
            protocol.delay(seconds=0.2)
            p1000.default_speed = 2.5
            p1000.dispense(20, qpcrplate[Y1].bottom(z=1.75), rate=0.25)
            protocol.delay(seconds=0.2)
            p1000.default_speed = 400
            p1000.move_to(qpcrplate[Y2].top(z=1.0))
            protocol.delay(seconds=0.2)
            p1000.default_speed = 2.5
            p1000.dispense(20, qpcrplate[Y2].bottom(z=1.75), rate=0.25)
            protocol.delay(seconds=0.2)
            p1000.default_speed = 400
            p1000.move_to(qpcrplate[Y3].top(z=1.0))
            protocol.delay(seconds=0.2)
            p1000.default_speed = 2.5
            p1000.dispense(20, qpcrplate[Y3].bottom(z=1.75), rate=0.25)
            protocol.delay(seconds=0.2)
            p1000.default_speed = 400
            p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
            if samplecolumns >= 1:#-----------------------------------------------------------------------------------------
                X = 'A10'
                Y1 = 'B1'
                Y2 = 'B2'
                Y3 = 'B3' 
                p1000.pick_up_tip()
                p1000.move_to(dilution_plate[X].bottom(z=0.1))
                p1000.mix(30,58)
                p1000.aspirate(62, dilution_plate[X].bottom(z=0.1), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.move_to(qpcrplate[Y1].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y1].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.move_to(qpcrplate[Y2].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y2].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.move_to(qpcrplate[Y3].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y3].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
            if samplecolumns >= 2:#-----------------------------------------------------------------------------------------
                X = 'A11'
                Y1 = 'A4'
                Y2 = 'A5'
                Y3 = 'A6' 
                p1000.pick_up_tip()
                p1000.move_to(dilution_plate[X].bottom(z=0.1))
                p1000.mix(30,58)
                p1000.aspirate(62, dilution_plate[X].bottom(z=0.1), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.move_to(qpcrplate[Y1].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y1].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.move_to(qpcrplate[Y2].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y2].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.move_to(qpcrplate[Y3].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y3].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()
            if samplecolumns >= 3:#-----------------------------------------------------------------------------------------
                X = 'A12'
                Y1 = 'B4'
                Y2 = 'B5'
                Y3 = 'B6' 
                p1000.pick_up_tip()
                p1000.move_to(dilution_plate[X].bottom(z=0.1))
                p1000.mix(30,58)
                p1000.aspirate(62, dilution_plate[X].bottom(z=0.1), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.move_to(qpcrplate[Y1].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y1].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.move_to(qpcrplate[Y2].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y2].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.move_to(qpcrplate[Y3].top(z=1.0))
                protocol.delay(seconds=0.2)
                p1000.default_speed = 2.5
                p1000.dispense(20, qpcrplate[Y3].bottom(z=1.75), rate=0.25)
                protocol.delay(seconds=0.2)
                p1000.default_speed = 400
                p1000.drop_tip() if DRYRUN == 'NO' else p1000.return_tip()