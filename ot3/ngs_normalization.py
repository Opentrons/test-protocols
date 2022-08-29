import inspect

from opentrons import protocol_api, types

metadata = {
    "protocolName": "NGS NORMALIZE",
    "author": "Opentrons <protocols@opentrons.com>",
    "source": "Protocol Library",
    "apiLevel": "2.9",
}


def right(s, amount):
    if s == None:
        return None
    elif amount == None:
        return None  # Or throw a missing argument error
    s = str(s)
    if amount > len(s):
        return s
    elif amount == 0:
        return ""
    else:
        return s[-amount:]


# settings
DRYRUN = "NO"  # YES or NO, DRYRUN = 'YES' will return tips, skip incubation times, shorten mix, for testing purposes
# this protocol does not actually use modules
NOMODULES = "YES"  # YES or NO, NOMODULES = 'YES' will not require modules on the deck and will skip module steps, for testing purposes, if DRYRUN = 'YES', then NOMODULES will automatically set itself to 'NO'
TIPREUSE = "NO"  # YES or NO, Reusing tips on wash steps reduces tips needed, no tip refill needed, suggested only for 24x run with all steps
OFFSET = "YES"  # YES or NO, Sets whether to use protocol specific z offsets for each tip and labware or no offsets aside from defaults


def run(protocol: protocol_api.ProtocolContext):

    if DRYRUN == "YES":
        protocol.comment("THIS IS A DRY RUN")
    else:
        protocol.comment("THIS IS A REACTION RUN")

    # labware
    if NOMODULES == "YES":
        protocol.comment("THIS IS A NO MODULE RUN")
        reservoir = protocol.load_labware("nest_12_reservoir_15ml", "2")
        tiprack_200_1 = protocol.load_labware("opentrons_ot3_96_tiprack_1000ul", "5")
        sample_plate = protocol.load_labware(
            "nest_96_wellplate_100ul_pcr_full_skirt", "7"
        )
        tiprack_200_X = protocol.load_labware("opentrons_ot3_96_tiprack_1000ul", "9")

    else:
        protocol.comment("THIS IS A MODULE RUN")
        mag_block = protocol.load_module("magnetic module gen2", "1")
        reservoir = protocol.load_labware("nest_12_reservoir_15ml", "2")
        temp_block = protocol.load_module("temperature module gen2", "3")
        tiprack_200_1 = protocol.load_labware("opentrons_96_filtertiprack_200ul", "5")
        thermocycler = protocol.load_module("thermocycler module")
        sample_plate = thermocycler.load_labware(
            "nest_96_wellplate_100ul_pcr_full_skirt"
        )
        tiprack_200_X = protocol.load_labware("opentrons_96_filtertiprack_200ul", "9")

    # reagent
    RSB = reservoir["A6"]

    # pipette
    if NOMODULES == "NO":
        p300 = protocol.load_instrument(
            "p1000_multi_gen3", "right", tip_racks=[tiprack_200_1]
        )
        p20 = protocol.load_instrument("p50_multi_gen3", "left")
    else:
        p300 = protocol.load_instrument(
            "p1000_multi_gen3", "right", tip_racks=[tiprack_200_1]
        )
        p20 = protocol.load_instrument("p50_multi_gen3", "left")

    MaxTubeVol = 200
    RSBUsed = 0
    RSBVol = 0

    # samples
    src_file_path = inspect.getfile(lambda: None)
    protocol.comment(src_file_path)

    sample_quant_csv = """
    Sample_Plate, Sample_well,InitialVol,InitialConc,TargetConc
    sample_plate,A1,5,35.6,1
    sample_plate,B1,5,31.5,1
    sample_plate,C1,5,33.7,1
    sample_plate,D1,5,28.9,1
    sample_plate,E1,5,28.9,1
    sample_plate,F1,5,26.5,1
    sample_plate,G1,5,26.2,1
    sample_plate,H1,5,18.9,1
    sample_plate,A2,5,12.5,1
    sample_plate,B2,5,18.4,1
    sample_plate,C2,5,13,1
    sample_plate,D2,5,14.8,1
    sample_plate,E2,5,13.3,1
    sample_plate,F2,5,12.8,1
    sample_plate,G2,5,15.2,1
    sample_plate,H2,5,8.89,1
    sample_plate,A3,5,14,1
    sample_plate,B3,5,19.5,1
    sample_plate,C3,5,18.9,1
    sample_plate,D3,5,21,1
    sample_plate,E3,5,23.8,1
    sample_plate,F3,5,12.9,1
    sample_plate,G3,5,16.7,1
    sample_plate,H3,5,20,1
    sample_plate,A4,10,2.88,1
    sample_plate,B4,10,2.36,1
    sample_plate,C4,10,2.04,1
    sample_plate,D4,10,2.57,1
    sample_plate,E4,10,2.47,1
    sample_plate,F4,10,2.09,1
    sample_plate,G4,10,2.47,1
    sample_plate,H4,10,3.18,1
    sample_plate,A5,10,3.2,1
    sample_plate,B5,10,4.12,1
    sample_plate,C5,10,3.18,1
    sample_plate,D5,10,2.6,1
    sample_plate,E5,10,4.47,1
    sample_plate,F5,10,2.99,1
    sample_plate,G5,10,2.97,1
    sample_plate,H5,10,2.93,1
    """

    data = [r.split(",") for r in sample_quant_csv.strip().splitlines() if r][1:]

    # offset
    if OFFSET == "YES":
        p300_offset_Res = 2
        p300_offset_Thermo = 1
        p300_offset_Mag = 0.70
        p300_offset_Deck = 0.3
        p300_offset_Temp = 0.65
        p300_offset_Tube = 0
        p20_offset_Res = 2
        p20_offset_Thermo = 1
        p20_offset_Mag = 0.75
        p20_offset_Deck = 0.3
        p20_offset_Temp = 0.85
        p20_offset_Tube = 0
    else:
        p300_offset_Res = 0
        p300_offset_Thermo = 0
        p300_offset_Mag = 0
        p300_offset_Deck = 0
        p300_offset_Temp = 0
        p300_offset_Tube = 0
        p20_offset_Res = 0
        p20_offset_Thermo = 0
        p20_offset_Mag = 0
        p20_offset_Deck = 0
        p20_offset_Temp = 0
        p20_offset_Tube = 0

    p300TIPS = [
        tiprack_200_1["H1"],
        tiprack_200_1["G1"],
        tiprack_200_1["F1"],
        tiprack_200_1["E1"],
        tiprack_200_1["D1"],
        tiprack_200_1["C1"],
        tiprack_200_1["B1"],
        tiprack_200_1["A1"],
        tiprack_200_1["H2"],
        tiprack_200_1["G2"],
        tiprack_200_1["F2"],
        tiprack_200_1["E2"],
        tiprack_200_1["D2"],
        tiprack_200_1["C2"],
        tiprack_200_1["B2"],
        tiprack_200_1["A2"],
        tiprack_200_1["H3"],
        tiprack_200_1["G3"],
        tiprack_200_1["F3"],
        tiprack_200_1["E3"],
        tiprack_200_1["D3"],
        tiprack_200_1["C3"],
        tiprack_200_1["B3"],
        tiprack_200_1["A3"],
        tiprack_200_1["H4"],
        tiprack_200_1["G4"],
        tiprack_200_1["F4"],
        tiprack_200_1["E4"],
        tiprack_200_1["D4"],
        tiprack_200_1["C4"],
        tiprack_200_1["B4"],
        tiprack_200_1["A4"],
        tiprack_200_1["H5"],
        tiprack_200_1["G5"],
        tiprack_200_1["F5"],
        tiprack_200_1["E5"],
        tiprack_200_1["D5"],
        tiprack_200_1["C5"],
        tiprack_200_1["B5"],
        tiprack_200_1["A5"],
        tiprack_200_1["H6"],
        tiprack_200_1["G6"],
        tiprack_200_1["F6"],
        tiprack_200_1["E6"],
        tiprack_200_1["D6"],
        tiprack_200_1["C6"],
        tiprack_200_1["B6"],
        tiprack_200_1["A6"],
        tiprack_200_1["H7"],
        tiprack_200_1["G7"],
        tiprack_200_1["F7"],
        tiprack_200_1["E7"],
        tiprack_200_1["D7"],
        tiprack_200_1["C7"],
        tiprack_200_1["B7"],
        tiprack_200_1["A7"],
        tiprack_200_1["H8"],
        tiprack_200_1["G8"],
        tiprack_200_1["F8"],
        tiprack_200_1["E8"],
        tiprack_200_1["D8"],
        tiprack_200_1["C8"],
        tiprack_200_1["B8"],
        tiprack_200_1["A8"],
        tiprack_200_1["H9"],
        tiprack_200_1["G9"],
        tiprack_200_1["F9"],
        tiprack_200_1["E9"],
        tiprack_200_1["D9"],
        tiprack_200_1["C9"],
        tiprack_200_1["B9"],
        tiprack_200_1["A9"],
        tiprack_200_1["H10"],
        tiprack_200_1["G10"],
        tiprack_200_1["F10"],
        tiprack_200_1["E10"],
        tiprack_200_1["D10"],
        tiprack_200_1["C10"],
        tiprack_200_1["B10"],
        tiprack_200_1["A10"],
        tiprack_200_1["H11"],
        tiprack_200_1["G11"],
        tiprack_200_1["F11"],
        tiprack_200_1["E11"],
        tiprack_200_1["D11"],
        tiprack_200_1["C11"],
        tiprack_200_1["B11"],
        tiprack_200_1["A11"],
        tiprack_200_1["H12"],
        tiprack_200_1["G12"],
        tiprack_200_1["F12"],
        tiprack_200_1["E12"],
        tiprack_200_1["D12"],
        tiprack_200_1["C12"],
        tiprack_200_1["B12"],
        tiprack_200_1["A12"],
    ]

    p300TIPX = [
        tiprack_200_X["H1"],
        tiprack_200_X["G1"],
        tiprack_200_X["F1"],
        tiprack_200_X["E1"],
        tiprack_200_X["D1"],
        tiprack_200_X["C1"],
        tiprack_200_X["B1"],
        tiprack_200_X["A1"],
        tiprack_200_X["H2"],
        tiprack_200_X["G2"],
        tiprack_200_X["F2"],
        tiprack_200_X["E2"],
        tiprack_200_X["D2"],
        tiprack_200_X["C2"],
        tiprack_200_X["B2"],
        tiprack_200_X["A2"],
        tiprack_200_X["H3"],
        tiprack_200_X["G3"],
        tiprack_200_X["F3"],
        tiprack_200_X["E3"],
        tiprack_200_X["D3"],
        tiprack_200_X["C3"],
        tiprack_200_X["B3"],
        tiprack_200_X["A3"],
        tiprack_200_X["H4"],
        tiprack_200_X["G4"],
        tiprack_200_X["F4"],
        tiprack_200_X["E4"],
        tiprack_200_X["D4"],
        tiprack_200_X["C4"],
        tiprack_200_X["B4"],
        tiprack_200_X["A4"],
        tiprack_200_X["H5"],
        tiprack_200_X["G5"],
        tiprack_200_X["F5"],
        tiprack_200_X["E5"],
        tiprack_200_X["D5"],
        tiprack_200_X["C5"],
        tiprack_200_X["B5"],
        tiprack_200_X["A5"],
        tiprack_200_X["H6"],
        tiprack_200_X["G6"],
        tiprack_200_X["F6"],
        tiprack_200_X["E6"],
        tiprack_200_X["D6"],
        tiprack_200_X["C6"],
        tiprack_200_X["B6"],
        tiprack_200_X["A6"],
        tiprack_200_X["H7"],
        tiprack_200_X["G7"],
        tiprack_200_X["F7"],
        tiprack_200_X["E7"],
        tiprack_200_X["D7"],
        tiprack_200_X["C7"],
        tiprack_200_X["B7"],
        tiprack_200_X["A7"],
        tiprack_200_X["H8"],
        tiprack_200_X["G8"],
        tiprack_200_X["F8"],
        tiprack_200_X["E8"],
        tiprack_200_X["D8"],
        tiprack_200_X["C8"],
        tiprack_200_X["B8"],
        tiprack_200_X["A8"],
        tiprack_200_X["H9"],
        tiprack_200_X["G9"],
        tiprack_200_X["F9"],
        tiprack_200_X["E9"],
        tiprack_200_X["D9"],
        tiprack_200_X["C9"],
        tiprack_200_X["B9"],
        tiprack_200_X["A9"],
        tiprack_200_X["H10"],
        tiprack_200_X["G10"],
        tiprack_200_X["F10"],
        tiprack_200_X["E10"],
        tiprack_200_X["D10"],
        tiprack_200_X["C10"],
        tiprack_200_X["B10"],
        tiprack_200_X["A10"],
        tiprack_200_X["H11"],
        tiprack_200_X["G11"],
        tiprack_200_X["F11"],
        tiprack_200_X["E11"],
        tiprack_200_X["D11"],
        tiprack_200_X["C11"],
        tiprack_200_X["B11"],
        tiprack_200_X["A11"],
        tiprack_200_X["H12"],
        tiprack_200_X["G12"],
        tiprack_200_X["F12"],
        tiprack_200_X["E12"],
        tiprack_200_X["D12"],
        tiprack_200_X["C12"],
        tiprack_200_X["B12"],
        tiprack_200_X["A12"],
    ]

    protocol.comment("==============================================")
    protocol.comment("Reading File")
    protocol.comment("==============================================")

    current = 0
    while current < len(data):

        CurrentWell = str(data[current][1])
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
        TotalDNA = float(InitialConc * InitialVol)
        if TargetConc > 0:
            TargetVol = float(TotalDNA / TargetConc)
        else:
            TargetVol = InitialVol
        if TargetVol > InitialVol:
            DilutionVol = float(TargetVol - InitialVol)
        else:
            DilutionVol = 0
        FinalVol = float(DilutionVol + InitialVol)
        if TotalDNA > 0 and FinalVol > 0:
            FinalConc = float(TotalDNA / FinalVol)
        else:
            FinalConc = 0

        if DilutionVol <= 1:
            protocol.comment("Sample " + CurrentWell + ": Conc. Too Low, Will Skip")
        elif DilutionVol > MaxTubeVol - InitialVol:
            DilutionVol = MaxTubeVol - InitialVol
            protocol.comment(
                "Sample "
                + CurrentWell
                + ": Conc. Too High, Will add, "
                + str(DilutionVol)
                + "ul, Max = "
                + str(MaxTubeVol)
                + "ul"
            )
            RSBVol += MaxTubeVol - InitialVol
        else:
            protocol.comment(
                "Sample "
                + CurrentWell
                + ": Using p300, will add "
                + str(round(DilutionVol, 1))
            )
            RSBVol += DilutionVol
        current += 1

    if RSBVol >= 14000:
        protocol.pause("Caution, more than 15ml Required")
    else:
        protocol.comment("RSB Minimum: " + str(round(RSBVol / 1000, 1) + 2) + "ml")

    protocol.comment("==============================================")
    protocol.comment("Normalizing Samples")
    protocol.comment("==============================================")

    p300TIPCOUNT = 0
    p300TIPDROP = 0

    current = 0
    while current < len(data):

        CurrentWell = str(data[current][1])
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
        TotalDNA = float(InitialConc * InitialVol)
        if TargetConc > 0:
            TargetVol = float(TotalDNA / TargetConc)
        else:
            TargetVol = InitialVol
        if TargetVol > InitialVol:
            DilutionVol = float(TargetVol - InitialVol)
        else:
            DilutionVol = 0
        FinalVol = float(DilutionVol + InitialVol)
        if TotalDNA > 0 and FinalVol > 0:
            FinalConc = float(TotalDNA / FinalVol)
        else:
            FinalConc = 0

        protocol.comment(
            "Number " + str(data[current]) + ": Sample " + str(CurrentWell)
        )

        if DilutionVol <= 0:
            # If the No Volume
            protocol.comment("Conc. Too Low, Skipping")

        elif DilutionVol >= MaxTubeVol - InitialVol:
            # If the Required Dilution volume is >= Max Volume
            DilutionVol = MaxTubeVol - InitialVol
            protocol.comment(
                "Conc. Too High, Will add, "
                + str(DilutionVol)
                + "ul, Max = "
                + str(MaxTubeVol)
                + "ul"
            )
            protocol.pause()
            p300.pick_up_tip(p300TIPS[p300TIPCOUNT], presses=1, increment=0.5)
            protocol.pause()
            p300.aspirate(DilutionVol, RSB.bottom())
            protocol.pause()
            p300.dispense(DilutionVol, sample_plate.wells_by_name()[CurrentWell])
            protocol.pause()
            HighVolMix = 10
            for Mix in range(HighVolMix):
                p300.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                p300.aspirate(100)
                p300.move_to(sample_plate.wells_by_name()[CurrentWell].bottom())
                p300.aspirate(100)
                p300.dispense(100)
                p300.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                p300.dispense(100)
                Mix += 1
            p300.move_to(sample_plate.wells_by_name()[CurrentWell].top())
            protocol.delay(seconds=3)
            p300.blow_out()
            p300.drop_tip() if DRYRUN == "NO" else p300.drop_tip(p300TIPX[p300TIPDROP])
            p300TIPCOUNT += 1
            p300TIPDROP += 1
        else:
            protocol.comment("Using p300 to add " + str(round(DilutionVol, 1)))
            p300.pick_up_tip(p300TIPS[p300TIPCOUNT], presses=1, increment=0.5)
            p300.aspirate(DilutionVol, RSB.bottom())
            if DilutionVol + InitialVol >= 120:
                HighVolMix = 10
                p300.dispense(DilutionVol, sample_plate.wells_by_name()[CurrentWell])
                for Mix in range(HighVolMix):
                    p300.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                    p300.aspirate(100)
                    p300.move_to(sample_plate.wells_by_name()[CurrentWell].bottom())
                    p300.aspirate(DilutionVol + InitialVol - 100)
                    p300.dispense(100)
                    p300.move_to(sample_plate.wells_by_name()[CurrentWell].center())
                    p300.dispense(DilutionVol + InitialVol - 100)
                    Mix += 1
            else:
                p300.dispense(DilutionVol, sample_plate.wells_by_name()[CurrentWell])
                p300.move_to(sample_plate.wells_by_name()[CurrentWell].bottom())
                p300.mix(10, DilutionVol + InitialVol)
                p300.move_to(sample_plate.wells_by_name()[CurrentWell].top())
            protocol.delay(seconds=3)
            p300.blow_out()
            p300.drop_tip() if DRYRUN == "NO" else p300.drop_tip(p300TIPX[p300TIPDROP])
            p300TIPCOUNT += 1
            p300TIPDROP += 1

        current += 1

    protocol.comment("==============================================")
    protocol.comment("Results")
    protocol.comment("==============================================")

    current = 0
    while current < len(data):

        CurrentWell = str(data[current][1])
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
        TotalDNA = float(InitialConc * InitialVol)
        if TargetConc > 0:
            TargetVol = float(TotalDNA / TargetConc)
        else:
            TargetVol = InitialVol
        if TargetVol > InitialVol:
            DilutionVol = float(TargetVol - InitialVol)
        else:
            DilutionVol = 0
        if DilutionVol > MaxTubeVol - InitialVol:
            DilutionVol = MaxTubeVol - InitialVol
        FinalVol = float(DilutionVol + InitialVol)
        if TotalDNA > 0 and FinalVol > 0:
            FinalConc = float(TotalDNA / FinalVol)
        else:
            FinalConc = 0
        protocol.comment(
            "Sample "
            + CurrentWell
            + ": "
            + str(round(FinalVol, 1))
            + " at "
            + str(round(FinalConc, 1))
            + "ng/ul"
        )

        current += 1
