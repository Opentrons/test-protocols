from opentrons.protocol_api import COLUMN, EMPTY


requirements = {
	"robotType": "Flex",
	"apiLevel": "2.16"
}

def run(protocol_context):

	tip_rack1 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "B3")
	#tip_rack2 = protocol_context.load_labware("opentrons_flex_96_tiprack_50ul", "B3")
	
	instrument = protocol_context.load_instrument('flex_96channel_1000', mount="left", tip_racks=[tip_rack1])
	my_pcr_plate = protocol_context.load_labware('nest_96_wellplate_200ul_flat', "B2")
	my_other_pcr_plate = protocol_context.load_labware('nest_96_wellplate_200ul_flat', "C2")

	waste_chute = protocol_context.load_waste_chute()

	# This will set the 96 channel to use its last nozzle column to pick up tips.
	# This essentially configures the 96-channel to run as an 8-channel pipette
	# Currently 'column' with starting nozzle 'A12' is the only config available
	instrument.configure_nozzle_layout(style=COLUMN, start="A12")

	# will pick up tips from column 1 of tiprack, with column 12 nozzles
	instrument.pick_up_tip()

	# will aspirate 50uL in each tip from column 4 of my_pcr_plate.
	# labware to the left of my_pcr_plate shouldn't be taller than the height to which the 96-channel lowers down to
	instrument.aspirate(50, my_pcr_plate.wells_by_name()["A4"])

	# should error out because cannot move to partial column
	# instrument.dispense(30, other_labware.wells_by_name()["B5"])

	# # should error out because return tip not allowed in partial tip configuration
	# instrument.return_tip()

	# will drop tip in default trash (or waste chute)
	instrument.drop_tip(waste_chute)

