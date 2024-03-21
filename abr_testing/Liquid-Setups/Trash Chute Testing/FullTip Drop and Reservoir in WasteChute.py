from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL

metadata = {
    "protocolName": "FullTip and Reservoir in WasteChute",
    "author": "Rhyann Clarke <rhyann.clarke@opentrons.com>",
    "source": "Protocol Library",
}
requirements = {    
    "robotType": "Flex",
    "apiLevel": "2.16",
    
}

def run(protocol_context: protocol_api.ProtocolContext):
    
    adapter1 = protocol_context.load_adapter("opentrons_flex_96_tiprack_adapter", "A2")
    adapter2 = protocol_context.load_adapter("opentrons_flex_96_tiprack_adapter", "A3")

    # load the 1000 ul tipracks
    tiprack1000_1 = adapter1.load_labware("opentrons_flex_96_tiprack_50ul")
    tiprack1000_2 = adapter2.load_labware("opentrons_flex_96_tiprack_50ul")
    tiprack1000_3 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "B2")

    #load the 200 ul tipracks
    tiprack200_1 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "B3")
    tiprack200_2 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "A4")
    tiprack200_3 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "B4")

    #load the 50 ul tipracks
    tiprack50_1 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "C3")
    tiprack50_2 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "C4")
    tiprack50_3 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "D4")

    #load the labware
    nest_res_1 = protocol_context.load_labware('nest_1_reservoir_195ml', "B1")
    nest_res_2 = protocol_context.load_labware('nest_1_reservoir_195ml', "C2")
    nest_res_3 = protocol_context.load_labware('nest_1_reservoir_195ml', "C1")
    nest_res_4 = protocol_context.load_labware('nest_1_reservoir_195ml', "D1")
    nest_res_5 = protocol_context.load_labware('nest_1_reservoir_195ml', "D2")
    
    #load the 96 channel
    pipette = protocol_context.load_instrument(
        "flex_96channel_1000", mount="left", tip_racks=[tiprack1000_1, tiprack1000_2, tiprack1000_3, tiprack200_1, tiprack200_2, tiprack200_3, tiprack50_1, tiprack50_2, tiprack50_3]
    )

    # load the trashes
    wasteChute = protocol_context.load_waste_chute()
    trashA1 = protocol_context.load_trash_bin("A1") 
    
    #Perform protocol actions for tiprack 1
    pipette.configure_nozzle_layout(style=ALL, tip_racks=[tiprack1000_1])
    pipette.pick_up_tip(tiprack1000_1.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack1000_1, wasteChute, use_gripper=True)

    #Perform protocol actions for tiprack 2
    pipette.pick_up_tip(tiprack1000_2.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack1000_2, wasteChute, use_gripper=True)

    # Perform protocol actions for tiprack 3
    pipette.configure_nozzle_layout(style=COLUMN, start="A12")

    pipette.pick_up_tip(tiprack1000_3.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack1000_3, wasteChute, use_gripper=True)

    # Perform protocol actions for tiprack 4

    pipette.pick_up_tip(tiprack200_1.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack200_1, wasteChute, use_gripper=True)

    #Repopulate deck
    protocol_context.move_labware(tiprack200_2, adapter1, use_gripper=True)
    protocol_context.move_labware(tiprack200_3, adapter2, use_gripper=True)

    #Perform protocol actions for tiprack 5
    pipette.configure_nozzle_layout(style=ALL)
    pipette.pick_up_tip(tiprack200_2.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack200_2, wasteChute, use_gripper=True)
    
    #Perform protocol actions for tiprack 6
    pipette.pick_up_tip(tiprack200_3.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack200_3, wasteChute, use_gripper=True)
    
    # Move two 50 ul tip racks to adapters
    protocol_context.move_labware(tiprack50_2, adapter1, use_gripper=True)
    protocol_context.move_labware(tiprack50_3, adapter2, use_gripper=True)
    
    pipette.configure_nozzle_layout(style = ALL)
    
    pipette.pick_up_tip(tiprack50_2.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack50_2, wasteChute, use_gripper=True)

    # Perform protocol actions for tiprack 7
    pipette.configure_nozzle_layout(style=COLUMN, start="A12")
    pipette.pick_up_tip(tiprack50_1.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack50_1, wasteChute, use_gripper=True)
    
    # Repopulate last item
    protocol_context.move_labware(tiprack50_3, adapter1, use_gripper=True)

    # Perform protocol actions for tiprack 5
    pipette.configure_nozzle_layout(style=ALL)
    pipette.pick_up_tip(tiprack50_3.wells()[0])
    pipette.drop_tip()
    protocol_context.move_labware(tiprack50_3, wasteChute, use_gripper=True)

    #Clean the deck
    protocol_context.move_labware(nest_res_1, wasteChute, use_gripper=True)
    protocol_context.move_labware(nest_res_2, wasteChute, use_gripper=True)
    protocol_context.move_labware(nest_res_3, wasteChute, use_gripper=True)
    protocol_context.move_labware(nest_res_4, wasteChute, use_gripper=True)
    protocol_context.move_labware(nest_res_5, wasteChute, use_gripper=True)
    
    
