
from opentrons import protocol_api
from opentrons import types

import random

metadata = {
    'protocolName': 'Throw out Liquid Filled Plates- DEEP Well',
    'author': 'Rhyann clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
}
requirements = {
    'robotType': 'Flex',
    'apiLevel': '2.15'
}

def run(protocol: protocol_api.ProtocolContext):
    #PLATE = 'armadillo_96_wellplate_200ul_pcr_full_skirt' 
    PLATE = 'nest_96_wellplate_2ml_deep'
    
    
    plate_1        = protocol.load_labware(PLATE,'A1')  
    plate_2        = protocol.load_labware(PLATE,'A2') 
    plate_3        = protocol.load_labware(PLATE,'B1')
    plate_4        = protocol.load_labware(PLATE,'B2')
    def move_to_slot(labware, slot, p_x_off = 0, p_y_off = 0, p_z_off = 0, d_x_off = 0, d_y_off = 0, d_z_off = 0):
        protocol.move_labware(
            labware         = labware,
            new_location    = slot,
            use_gripper     = True,     
            pick_up_offset  = {"x": p_x_off, "y": p_y_off, "z": p_z_off},
            drop_offset     = {"x": d_x_off, "y": d_y_off, "z": d_z_off},
        )
        protocol.move_labware(labware=labware, new_location=protocol_api.OFF_DECK)
    D_Z_off_tiprack = 136.5 # Drop height for tip racks, caused pcr plate spillage
    D_Z_off_full_pcr_plate  = 90
    D_Z_off_full_deep_plate = 80
    pcr_plates = [plate_1, plate_2, plate_3, plate_4]
    for n in pcr_plates:
        move_to_slot(n, 3, d_y_off = -29, d_z_off = D_Z_off_full_pcr_plate)