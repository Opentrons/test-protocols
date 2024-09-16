import inspect
from dataclasses import replace
from opentrons import protocol_api, types
from opentrons import protocol_api
from opentrons.protocol_api import SINGLE


metadata = {
    'protocolName': 'Simple Normalize Long Right.py',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.20",
}


# settings
DRYRUN = True  # True or False, DRYRUN = True will return tips, skip incubation times, shorten mix, for testing purposes
MEASUREPAUSE = "NO"

ABR_TEST                = False
if ABR_TEST == True:
    DRYRUN              = True          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = False         # True = Used tips go in Trash, False = Used tips go back into rack
else:
    DRYRUN              = False          # True = skip incubation times, shorten mix, for testing purposes
    TIP_TRASH           = True 


def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_str(
        variable_name="mount_pos",
        display_name="Mount Position",
        description="What mount to use",
        choices=[
            {"display_name": "left_mount", "value": "left"},
            {"display_name": "right_mount", "value": "right"},
        ],
        default="right",
    )

    parameters.add_str(
        variable_name="pickup_direction",
        display_name="Pippette Pickup Method",
        description="Pick up by row or by column",
        choices=[
            {"display_name": "Row", "value": "row"},
            {"display_name": "Column", "value": "col"},
        ],
        default="row",
    )
    
    parameters.add_str(
        variable_name="tip_type",
        display_name="Tip Type",
        description="Type of tips being picked up",
        choices=[
            {"display_name": "50ul", "value": 'opentrons_flex_96_tiprack_50ul' },
            {"display_name": "200ul", "value": 'opentrons_flex_96_tiprack_200ul' },
            {"display_name": "1000ul", "value": 'opentrons_flex_96_tiprack_1000ul' },
        ],
        default='opentrons_flex_96_tiprack_200ul'
    )
def run(protocol: protocol_api.ProtocolContext):

    if DRYRUN == True:
        protocol.comment("THIS IS A DRY RUN")
    else:
        protocol.comment("THIS IS A REACTION RUN")

    direction = protocol.params.pickup_direction
    tip_type = protocol.params.tip_type
    # DECK SETUP AND LABWARE
    # ========== FIRST ROW ===========
    protocol.comment("THIS IS A NO MODULE RUN")
    tiprack_x_1   = protocol.load_labware(tip_type,  'D1')
    tiprack_x_2   = protocol.load_labware(tip_type,  'D2')
    sample_plate_1    = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", "D3")

    # ========== SECOND ROW ==========
    reservoir       = protocol.load_labware("nest_12_reservoir_15ml", "C1")
    sample_plate_2    = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", "C2")
    # ========== THIRD ROW ===========
    sample_plate_3    = protocol.load_labware("armadillo_96_wellplate_200ul_pcr_full_skirt", "B2")    
    # ========== FOURTH ROW ==========
    protocol.load_trash_bin("A3")

    # mount runtime parameter variable       
    mount_pos = protocol.params.mount_pos

    # reagent
    Dye_1     = reservoir["A1"]
    Dye_2     = reservoir["A2"]
    Dye_3     = reservoir["A3"]
    Diluent_1 = reservoir["A4"]
    Diluent_2 = reservoir["A5"]
    Diluent_3 = reservoir["A6"]

    # pipette
    p1000 = protocol.load_instrument("flex_8channel_1000", mount_pos)
    

    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    columns = range(12)
    current_rack = tiprack_x_1
    # CONFIGURE SINGLE LAYOUT
    p1000.configure_nozzle_layout(
        style=SINGLE,
        start="H1",
        # tip_racks=[tiprack_200_1,tiprack_200_2]
        )
    sample_quant_csv = """
    sample_plate_1, Sample_well,DYE,DILUENT
    sample_plate_1,A1,0,100
    sample_plate_1,B1,5,95
    sample_plate_1,C1,10,90
    sample_plate_1,D1,20,80
    sample_plate_1,E1,40,60
    sample_plate_1,F1,15,40
    sample_plate_1,G1,40,20
    sample_plate_1,H1,40,0
    sample_plate_1,A2,35,65
    sample_plate_1,B2,38,42
    sample_plate_1,C2,42,58
    sample_plate_1,D2,32,8
    sample_plate_1,E2,38,12
    sample_plate_1,F2,26,74
    sample_plate_1,G2,31,69
    sample_plate_1,H2,46,4
    sample_plate_1,A3,47,13
    sample_plate_1,B3,42,18
    sample_plate_1,C3,46,64
    sample_plate_1,D3,48,22
    sample_plate_1,E3,26,74
    sample_plate_1,F3,34,66
    sample_plate_1,G3,43,37
    sample_plate_1,H3,20,80
    sample_plate_1,A4,44,16
    sample_plate_1,B4,49,41
    sample_plate_1,C4,48,42
    sample_plate_1,D4,44,16
    sample_plate_1,E4,47,53
    sample_plate_1,F4,47,33
    sample_plate_1,G4,42,48
    sample_plate_1,H4,39,21
    sample_plate_1,A5,30,20
    sample_plate_1,B5,36,14
    sample_plate_1,C5,31,59
    sample_plate_1,D5,38,52
    sample_plate_1,E5,36,4
    sample_plate_1,F5,32,28
    sample_plate_1,G5,35,55
    sample_plate_1,H5,39,1
    sample_plate_1,A6,31,59
    sample_plate_1,B6,20,80
    sample_plate_1,C6,38,2
    sample_plate_1,D6,34,46
    sample_plate_1,E6,30,70
    sample_plate_1,F6,32,58
    sample_plate_1,G6,21,79
    sample_plate_1,H6,38,52
    sample_plate_1,A7,33,27
    sample_plate_1,B7,34,16
    sample_plate_1,C7,40,60
    sample_plate_1,D7,34,26
    sample_plate_1,E7,30,20
    sample_plate_1,F7,44,56
    sample_plate_1,G7,26,74
    sample_plate_1,H7,45,55
    sample_plate_1,A8,39,1
    sample_plate_1,B8,38,2
    sample_plate_1,C8,34,66
    sample_plate_1,D8,39,11
    sample_plate_1,E8,46,54
    sample_plate_1,F8,37,63
    sample_plate_1,G8,38,42
    sample_plate_1,H8,34,66
    sample_plate_1,A9,44,56
    sample_plate_1,B9,39,11
    sample_plate_1,C9,30,70
    sample_plate_1,D9,37,33
    sample_plate_1,E9,46,54
    sample_plate_1,F9,39,21
    sample_plate_1,G9,29,41
    sample_plate_1,H9,23,77
    sample_plate_1,A10,26,74
    sample_plate_1,B10,39,1
    sample_plate_1,C10,31,49
    sample_plate_1,D10,38,62
    sample_plate_1,E10,29,1
    sample_plate_1,F10,21,79
    sample_plate_1,G10,29,41
    sample_plate_1,H10,28,42
    sample_plate_1,A11,15,55
    sample_plate_1,B11,28,72
    sample_plate_1,C11,11,49
    sample_plate_1,D11,34,66
    sample_plate_1,E11,27,73
    sample_plate_1,F11,30,40
    sample_plate_1,G11,33,67
    sample_plate_1,H11,31,39
    sample_plate_1,A12,39,31
    sample_plate_1,B12,47,53
    sample_plate_1,C12,46,54
    sample_plate_1,D12,13,7
    sample_plate_1,E12,34,46
    sample_plate_1,F12,45,35
    sample_plate_1,G12,28,42
    sample_plate_1,H12,37,63
    """

    data = [r.split(",") for r in sample_quant_csv.strip().splitlines() if r][1:]


    

    for X in range(1):
        protocol.comment("==============================================")
        protocol.comment("Adding Dye Sample Plate 1")
        protocol.comment("==============================================")

        current = 0
        col_ind = 1
        row_ind = 0

        def move(col_ind, row_ind, current_rack):
            if direction == "row":
                if col_ind >= 12:
                    if row_ind >= 7:
                        if current_rack == tiprack_x_1:
                            current_rack = tiprack_x_2
                            col_ind = 1
                            row_ind = 0
                    else:
                        row_ind += 1
                        col_ind = 1
                else:
                    col_ind += 1
            elif direction == "col":
                if row_ind >= 7:
                    if col_ind >= 12:
                        if current_rack == tiprack_x_1:
                            current_rack = tiprack_x_2
                            col_ind = 1
                            row_ind = 0
                    else:
                        col_ind += 1
                        row_ind = 0
                else:
                    row_ind += 1
            return [col_ind, row_ind, current_rack]

        p1000.pick_up_tip(current_rack[rows[row_ind] + str(col_ind)])
        while current < len(data):
            CurrentWell = str(data[current][1])
            DyeVol = float(data[current][2])
            if DyeVol != 0 and DyeVol < 100:
                p1000.transfer(DyeVol, Dye_1.bottom(z=2), sample_plate_1.wells_by_name()[CurrentWell].top(z=1), new_tip='never')
            current += 1
        p1000.blow_out()
        p1000.touch_tip()
        p1000.drop_tip()

        updated = move(col_ind, row_ind, current_rack)
        col_ind = updated[0]
        row_ind = updated[1]
        current_rack = updated[2]

        protocol.comment("==============================================")
        protocol.comment("Adding Diluent Sample Plate 1")
        protocol.comment("==============================================")

        current = 0
        while current < len(data):
            CurrentWell = str(data[current][1])
            DilutionVol = float(data[current][2])
            if DilutionVol != 0 and DilutionVol < 100:
                p1000.pick_up_tip(current_rack[rows[row_ind] + str(col_ind)])
                p1000.aspirate(DilutionVol, Diluent_1.bottom(z=2))
                p1000.dispense(DilutionVol, sample_plate_1.wells_by_name()[CurrentWell].top(z=0.2))
                p1000.blow_out()
                p1000.touch_tip()
                p1000.drop_tip()
                updated = move(col_ind, row_ind, current_rack)
                col_ind = updated[0]
                row_ind = updated[1]
                current_rack = updated[2]

            current += 1

        protocol.comment("==============================================")
        protocol.comment("Adding Dye Sample Plate 2")
        protocol.comment("==============================================")

        current = 0
        p1000.pick_up_tip(current_rack[rows[row_ind] + str(col_ind)])
        while current < len(data):
            CurrentWell = str(data[current][1])
            DyeVol = float(data[current][2])
            if DyeVol != 0 and DyeVol < 100:
                p1000.transfer(DyeVol, Dye_2.bottom(z=2), sample_plate_2.wells_by_name()[CurrentWell].top(z=1), new_tip='never')
            current += 1
        p1000.blow_out()
        p1000.touch_tip()
        p1000.drop_tip()
        updated = move(col_ind, row_ind, current_rack)
        col_ind = updated[0]
        row_ind = updated[1]
        current_rack = updated[2]

        protocol.comment("==============================================")
        protocol.comment("Adding Diluent Sample Plate 2")
        protocol.comment("==============================================")

        current = 0
        while current < len(data):
            CurrentWell = str(data[current][1])
            DilutionVol = float(data[current][2])
            if DilutionVol != 0 and DilutionVol < 100:
                p1000.pick_up_tip(current_rack[rows[row_ind] + str(col_ind)])
                p1000.aspirate(DilutionVol, Diluent_2.bottom(z=2))
                p1000.dispense(DilutionVol, sample_plate_2.wells_by_name()[CurrentWell].top(z=0.2))
                p1000.blow_out()
                p1000.touch_tip()
                p1000.drop_tip()
                updated = move(col_ind, row_ind, current_rack)
                col_ind = updated[0]
                row_ind = updated[1]
                current_rack = updated[2]
            current += 1

        protocol.comment("==============================================")
        protocol.comment("Adding Dye Sample Plate 3")
        protocol.comment("==============================================")

        current = 0
        p1000.pick_up_tip(current_rack[rows[row_ind] + str(col_ind)])
        while current < len(data):
            CurrentWell = str(data[current][1])
            DyeVol = float(data[current][2])
            if DyeVol != 0 and DyeVol < 100:
                p1000.transfer(DyeVol, Dye_3.bottom(z=2), sample_plate_3.wells_by_name()[CurrentWell].top(z=1), new_tip='never')
            current += 1
        p1000.blow_out()
        p1000.touch_tip()
        p1000.drop_tip()
        updated = move(col_ind, row_ind, current_rack)
        col_ind = updated[0]
        row_ind = updated[1]
        current_rack = updated[2]

        protocol.comment("==============================================")
        protocol.comment("Adding Diluent Sample Plate 3")
        protocol.comment("==============================================")

        current = 0
