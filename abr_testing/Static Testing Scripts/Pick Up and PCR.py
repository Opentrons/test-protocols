from opentrons import protocol_api
from opentrons import types


metadata = {
    'protocolName': 'PCR Plate Test',
    'author': 'Nick Shiland <nicholas.shiland@opentrons.com>',
    'source': 'Protocol Library'
    }


requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.18",
}

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE    
    tiprack_1        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'A1')
    tiprack_2        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'B1')
    tiprack_3        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'C1')
    tiprack_4        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'A2')
    tiprack_5        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'B2')
    pcr_plate        = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', location = 'B4')
    reservoir        = protocol.load_labware('nest_12_reservoir_15ml', location = 'D4')

    # Pipette
    pleft = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_1,tiprack_2, tiprack_3, tiprack_4, tiprack_5])
   
    for i in list(range(5)):
        for i in list(range(60)):
            pleft.pick_up_tip()
            pleft.aspirate(40, pcr_plate["A1"])
            pleft.move_to(reservoir["A1"].bottom())
            pleft.dispense(50, pcr_plate["A1"], touch_tip = True)
            pleft.return_tip()
        pleft.reset_tipracks()

    #pcr_plate["A1"].top()
        

    #touch tip with z offset using fur inside a 1well
