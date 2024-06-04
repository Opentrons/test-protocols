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
def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_int(
        variable_name="repetitions",
        display_name="Cycle Repetitions",
        description="Set Number of Times to Repeat Cycle",
        default = 5,
        minimum = 1,
        maximum = 150,
        unit = "times",
    )

def run(protocol: protocol_api.ProtocolContext):
    # DECK SETUP AND LABWARE    
    tiprack_1        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'A1')
    tiprack_2        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'B1')
    tiprack_3        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'C1')
    tiprack_4        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'A2')
    tiprack_5        = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = 'B2')
    pcr_plate        = protocol.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt', location = 'B3')
    reservoir        = protocol.load_labware('nest_12_reservoir_15ml', location = 'D3')
    repetitions = protocol.params.repetitions
    # Pipette
    pleft = protocol.load_instrument("flex_8channel_1000", "left", tip_racks=[tiprack_1,tiprack_2, tiprack_3, tiprack_4, tiprack_5])
   
   
    for i in list(range(repetitions)):
        for i in list(range(60)):
            pleft.transfer(
                volume=50,
                dest=pcr_plate["A1"],
                source=reservoir["A1"],
                touch_tip=True,
                trash = False,
            )
        pleft.reset_tipracks()

    #pcr_plate["A1"].top()
    #add mix
        
        #pleft.aspirate(40, pcr_plate["A1"])
        #pleft.move_to(reservoir["A1"].bottom())
        #pleft.dispense(40, pcr_plate["A1"])
    #touch tip with z offset using fur inside a 1well
