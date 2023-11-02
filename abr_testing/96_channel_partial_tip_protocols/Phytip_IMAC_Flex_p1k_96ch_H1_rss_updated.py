from opentrons.protocol_api import COLUMN, EMPTY


metadata = {
    'protocolName': 'Biotage PhyTip IMAC Columns - Flex w/ 96 channel pipette (partial tip configuration)',
    'author': 'Boren Lin, Opentrons',
    'source': ''
}

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.16",
}

NUM_SAMPLE = 24

global cols
cols = int(NUM_SAMPLE*2//8)
if NUM_SAMPLE*2%8 != 0: cols = cols + 1

# liquid volume uL 
VOL_EQL = 1000
VOL_SAMPLE = 500
VOL_WASH1 = 1000
VOL_WASH2 = 1000
VOL_ELN = 500

CYCLES_EQL = 2
CYCLES_SAMPLE = 6
CYCLES_WASH1 = 2
CYCLES_WASH2 = 2
CYCLES_ELN = 6

# pipet flow rate uL/s 
FLOWRATE_EQL = 8
FLOWRATE_SAMPLE = 4
FLOWRATE_WASH1 = 8
FLOWRATE_WASH2 = 8
FLOWRATE_ELN = 4

def run(ctx):

    # load labware and pipette
    phytiprack = ctx.load_labware('opentrons_flex_96_tiprack_1000ul', 'B3')  
    m1k = ctx.load_instrument('flex_96channel_1000', 'left', tip_racks=[phytiprack]) 
    m1k.configure_nozzle_layout(style=COLUMN, start="A12")

    default_rate = 700
    m1k.flow_rate.aspirate = default_rate
    m1k.flow_rate.dispense = default_rate 

    sample_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'D1', 'samples plate')
    equilibration_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'C1', 'equilibration plate')
    wash1_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'C2', 'wash plate 1')
    wash2_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'B2', 'wash plate 2')
    elution_plate = ctx.load_labware('nest_96_wellplate_2ml_deep', 'A2', 'elute plate')
    placeholder_labware_for_height = ctx.load_adapter('opentrons_flex_96_tiprack_adapter', "A1")

    sample = sample_plate.rows()[0][:cols]
    eql = equilibration_plate.rows()[0][:cols]
    wash1 = wash1_plate.rows()[0][:cols]
    wash2 = wash2_plate.rows()[0][:cols]
    eln = elution_plate.rows()[0][:cols]
    waste_chute = ctx.load_waste_chute()

    # mix sequences
    def plate_mix(cycles, volume, loc, rate, delay=20): # Changed delay from 20 to 0 for test run
        # m1k.flow_rate.aspirate = rate    # Uncomment for real run
        # m1k.flow_rate.dispense = rate    # Uncomment for real run
        for _ in range(cycles):
            m1k.aspirate(volume*0.9, loc.bottom(z=1))
            ctx.delay(seconds=delay)
            m1k.dispense(volume*0.9, loc.bottom(z=1))
            ctx.delay(seconds=0)   # Changed delay from 10 to 0 for test run
        m1k.move_to(loc.top(z=5))
        ctx.delay(seconds=0)       # Changed delay from 10 to 0 for test run

    # perform
    for i in range(cols):
        # Workaround for not having tip tracking for partial tip yet
        tip_column = "A"+ str(i+1)

        m1k.pick_up_tip(phytiprack.wells_by_name()[tip_column])
        plate_mix(CYCLES_EQL, VOL_EQL, eql[i], FLOWRATE_EQL)
        plate_mix(CYCLES_SAMPLE, VOL_SAMPLE, sample[i], FLOWRATE_SAMPLE)
        plate_mix(CYCLES_WASH1, VOL_WASH1, wash1[i], FLOWRATE_WASH1)
        plate_mix(CYCLES_WASH2, VOL_WASH2, wash2[i], FLOWRATE_WASH2)
        plate_mix(CYCLES_ELN, VOL_ELN, eln[i], FLOWRATE_ELN)
        m1k.drop_tip(waste_chute)
