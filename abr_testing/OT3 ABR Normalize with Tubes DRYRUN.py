from opentrons import protocol_api
from opentrons import types

metadata = {
    'protocolName': 'OT3 ABR Normalize with Tubes.py DRYRUN',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "OT-3",
    'apiLevel': '2.18',
}

# SCRIPT SETTINGS
ABR_TEST            = True
if ABR_TEST == True:
    DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack
else:
    DRYRUN              = False          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = True   

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_str(
        variable_name="left_pipette",
        display_name="Pipette Type Left Mount",
        description="Set Left Pipette Type",
        choices=[
        {"display_name": "1-Channel 50 µL", "value": "flex_1channel_50"},
        {"display_name": "1-Channel 1000 µL", "value": "flex_1channel_1000"},
    ],
    default = "flex_1channel_1000"
    )
    parameters.add_str(
        variable_name="right_pipette",
        display_name="Pipette Type Right Mount",
        description="Set Right Pipette Type",
        choices=[
        {"display_name": "1-Channel 50 µL", "value": "flex_1channel_50"},
        {"display_name": "1-Channel 1000 µL", "value": "flex_1channel_1000"},
    ],
    default = "flex_1channel_50"
    )

def run(protocol: protocol_api.ProtocolContext):
    left_pipette = protocol.params.left_pipette
    right_pipette = protocol.params.right_pipette
    if DRYRUN == True:
        protocol.comment("THIS IS A DRY RUN")
    else:
        protocol.comment("THIS IS A REACTION RUN")

   # labware
    tiprack_50_1    = protocol.load_labware('opentrons_flex_96_tiprack_50ul', '1')
    tiprack_200_1   = protocol.load_labware('opentrons_flex_96_tiprack_200ul', '4')
    reagent_tube    = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical','5')
    sample_plate    = protocol.load_labware('armadillo_96_wellplate_200ul_pcr_full_skirt','2')

    # reagent
    RSB               = reagent_tube.wells()[0]

    # pipette    
    if right_pipette == "flex_1channel_50":
        right_tiprack = tiprack_50_1
    else:
        right_tiprack = tiprack_200_1
    if left_pipette == "flex_1channel_1000":
        left_tiprack = tiprack_200_1
    else:
        left_tiprack = tiprack_50_1
        
    p_right    = protocol.load_instrument(right_pipette, 'right', tip_racks=[right_tiprack])
    p_left     = protocol.load_instrument(left_pipette, 'left', tip_racks=[left_tiprack])

    MaxTubeVol      = 200
    RSBUsed         = 0
    RSBVol          = 0

    sample_quant_csv = """
    Sample_Plate, Sample_well,InitialVol,InitialConc,TargetConc
    sample_plate,A2,10,3.94,1
    sample_plate,B2,10,3.5,1
    sample_plate,C2,10,3.46,1
    sample_plate,D2,10,3.1,1
    sample_plate,E2,10,2.64,1
    sample_plate,F2,10,3.16,1
    sample_plate,G2,10,2.9,1
    sample_plate,H2,10,2.8,1
    sample_plate,A3,10,2.82,1
    sample_plate,B3,10,2.84,1
    sample_plate,C3,10,2.72,1
    sample_plate,D3,10,2.9,1
    sample_plate,A5,10,3.94,1
    sample_plate,B5,10,3.5,1
    sample_plate,C5,10,3.46,1
    sample_plate,D5,10,3.1,1
    sample_plate,E5,10,2.64,1
    sample_plate,F5,10,3.16,1
    sample_plate,G5,10,2.9,1
    sample_plate,H5,10,2.8,1
    sample_plate,A6,10,2.82,1
    sample_plate,B6,10,2.84,1
    sample_plate,C6,10,2.72,1
    sample_plate,D6,10,2.9,1
    """

    data = [r.split(',') for r in sample_quant_csv.strip().splitlines() if r][1:]

    # commands

    protocol.comment('==============================================')
    protocol.comment('Reading File')
    protocol.comment('==============================================')

    current = 0
    while current < len(data):

        CurrentWell     = str(data[current][1])
        if float(data[current][2]) > 0:
            InitialVol = float(data[current][2])
        else:
            InitialVol = 0
        if float(data[current][3]) > 0:
            InitialConc = float(data[current][3])
        else:
            InitialConc = 0
        if float(data[current][4]) > 0:
            TargetConc = float(data[current][4])
        else:
            TargetConc = 0
        TotalDNA        = float(InitialConc*InitialVol)
        if TargetConc > 0:
            TargetVol = float(TotalDNA/TargetConc)
        else:
            TargetVol = InitialVol
        if TargetVol > InitialVol:
            DilutionVol = float(TargetVol-InitialVol)
        else:
            DilutionVol = 0
        FinalVol        = float(DilutionVol+InitialVol)
        if TotalDNA > 0 and FinalVol > 0:
            FinalConc       = float(TotalDNA/FinalVol)
        else:
            FinalConc = 0
            
        if DilutionVol <= 1:
            protocol.comment("Sample "+CurrentWell+": Conc. Too Low, Will Skip")
        elif DilutionVol > MaxTubeVol-InitialVol:
            DilutionVol = MaxTubeVol-InitialVol
            protocol.comment("Sample "+CurrentWell+": Conc. Too High, Will add, "+str(DilutionVol)+"ul, Max = "+str(MaxTubeVol)+"ul")
            RSBVol += MaxTubeVol-InitialVol
        else:
            if DilutionVol <=20:
                protocol.comment("Sample "+CurrentWell+": Using p_left, will add "+str(round(DilutionVol,1)))
            elif DilutionVol > 20:
                protocol.comment("Sample "+CurrentWell+": Using p_right, will add "+str(round(DilutionVol,1)))
            RSBVol += DilutionVol
        current += 1

    if RSBVol >= 14000:
        protocol.pause("Caution, more than 15ml Required")
    else:
        protocol.comment("RSB Minimum: "+str(round(RSBVol/1000,1)+1)+"ml")
    
    PiR2 = 176.71
    InitialRSBVol = RSBVol
    RSBHeight = (InitialRSBVol/PiR2)+17.5

    protocol.pause("Proceed")
    protocol.comment('==============================================')
    protocol.comment('Normalizing Samples')
    protocol.comment('==============================================')
    
    current = 0
    while current < len(data):

        CurrentWell     = str(data[current][1])
        if float(data[current][2]) > 0:
            InitialVol = float(data[current][2])
        else:
            InitialVol = 0
        if float(data[current][3]) > 0:
            InitialConc = float(data[current][3])
        else:
            InitialConc = 0
        if float(data[current][4]) > 0:
            TargetConc = float(data[current][4])
        else:
            TargetConc = 0
        TotalDNA        = float(InitialConc*InitialVol)
        if TargetConc > 0:
            TargetVol = float(TotalDNA/TargetConc)
        else:
            TargetVol = InitialVol
        if TargetVol > InitialVol:
            DilutionVol = float(TargetVol-InitialVol)
        else:
            DilutionVol = 0
        FinalVol        = float(DilutionVol+InitialVol)
        if TotalDNA > 0 and FinalVol > 0:
            FinalConc       = float(TotalDNA/FinalVol)
        else:
            FinalConc = 0
            
        protocol.comment("Number "+str(data[current])+": Sample "+str(CurrentWell))
#        protocol.comment("Vol Height = "+str(round(RSBHeight,2)))
        HeightDrop = DilutionVol/PiR2
#        protocol.comment("Vol Drop = "+str(round(HeightDrop,2)))

        if DilutionVol <= 0:
        #If the No Volume
            protocol.comment("Conc. Too Low, Skipping")
        
        elif DilutionVol >= MaxTubeVol-InitialVol:
        #If the Required Dilution volume is >= Max Volume
            DilutionVol = MaxTubeVol-InitialVol
            protocol.comment("Conc. Too High, Will add, "+str(DilutionVol)+"ul, Max = "+str(MaxTubeVol)+"ul")
            p_right.pick_up_tip()
            p_right.aspirate(DilutionVol, RSB.bottom(RSBHeight-(HeightDrop)))
            RSBHeight -= HeightDrop
#            protocol.comment("New Vol Height = "+str(round(RSBHeight,2)))
            p_right.dispense(DilutionVol, sample_plate.wells_by_name()[CurrentWell])
            HighVolMix = 10
            for Mix in range(HighVolMix):
                p_right.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                p_right.aspirate(100)
                p_right.move_to(sample_plate.wells_by_name()[CurrentWell].bottom(.5)) #original = ()
                p_right.aspirate(100)
                p_right.dispense(100)
                p_right.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                p_right.dispense(100)
                Mix += 1
            p_right.move_to(sample_plate.wells_by_name()[CurrentWell].top())
            protocol.delay(seconds=3)
            p_right.blow_out()
            p_right.drop_tip() if DRYRUN == False else p_right.return_tip()
        
        else:
            if DilutionVol <= 20:
        #If the Required Dilution volume is <= 20ul
                protocol.comment("Using p_left to add "+str(round(DilutionVol,1)))
                p_left.pick_up_tip()
                if  round(float(data[current][3]),1) <= 20:
                    p_left.aspirate(DilutionVol, RSB.bottom(RSBHeight-(HeightDrop)))
                    RSBHeight -= HeightDrop
                else:
                    p_left.aspirate(20, RSB.bottom(RSBHeight-(HeightDrop)))
                    RSBHeight -= HeightDrop
                p_left.dispense(DilutionVol, sample_plate.wells_by_name()[CurrentWell])

                p_left.move_to(sample_plate.wells_by_name()[CurrentWell].bottom(z=.5)) #original = ()
        # Mix volume <=20ul
                if DilutionVol+InitialVol <= 20:
                    p_left.mix(10,DilutionVol+InitialVol)
                elif DilutionVol+InitialVol > 20:
                    p_left.mix(10,20)
                p_left.move_to(sample_plate.wells_by_name()[CurrentWell].top())
                protocol.delay(seconds=3)
                p_left.blow_out()
                p_left.drop_tip() if DRYRUN == False else p_left.return_tip()
            
            elif DilutionVol > 20:
        #If the required volume is >20
                protocol.comment("Using p_right to add "+str(round(DilutionVol,1)))
                p_right.pick_up_tip()
                p_right.aspirate(DilutionVol, RSB.bottom(RSBHeight-(HeightDrop)))
                RSBHeight -= HeightDrop
                if DilutionVol+InitialVol >= 120:
                    HighVolMix = 10
                    for Mix in range(HighVolMix):
                        p_right.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                        p_right.aspirate(100)
                        p_right.move_to(sample_plate.wells_by_name()[CurrentWell].bottom(z=.5)) #original = ()
                        p_right.aspirate(DilutionVol+InitialVol-100)
                        p_right.dispense(100)
                        p_right.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                        p_right.dispense(DilutionVol+InitialVol-100)
                        Mix += 1
                else:
                    p_right.dispense(DilutionVol, sample_plate.wells_by_name()[CurrentWell])
                    p_right.move_to(sample_plate.wells_by_name()[CurrentWell].bottom(z=.5)) #original = ()
                    p_right.mix(10,DilutionVol+InitialVol)
                    p_right.move_to(sample_plate.wells_by_name()[CurrentWell].top())
                protocol.delay(seconds=3)
                p_right.blow_out()
                p_right.drop_tip() if DRYRUN == False else p_right.return_tip()
        current += 1
    
    protocol.comment('==============================================')
    protocol.comment('Results')
    protocol.comment('==============================================')

    current = 0
    while current < len(data):

        CurrentWell     = str(data[current][1])
        if float(data[current][2]) > 0:
            InitialVol = float(data[current][2])
        else:
            InitialVol = 0
        if float(data[current][3]) > 0:
            InitialConc = float(data[current][3])
        else:
            InitialConc = 0
        if float(data[current][4]) > 0:
            TargetConc = float(data[current][4])
        else:
            TargetConc = 0
        TotalDNA        = float(InitialConc*InitialVol)
        if TargetConc > 0:
            TargetVol = float(TotalDNA/TargetConc)
        else:
            TargetVol = InitialVol
        if TargetVol > InitialVol:
            DilutionVol = float(TargetVol-InitialVol)
        else:
            DilutionVol = 0
        if DilutionVol > MaxTubeVol-InitialVol:
            DilutionVol = MaxTubeVol-InitialVol
        FinalVol        = float(DilutionVol+InitialVol)
        if TotalDNA > 0 and FinalVol > 0:
            FinalConc       = float(TotalDNA/FinalVol)
        else:
            FinalConc = 0
        protocol.comment("Sample "+CurrentWell+": "+str(round(FinalVol,1))+" at "+str(round(FinalConc,1))+"ng/ul")
        
        current += 1