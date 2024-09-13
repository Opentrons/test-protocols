from opentrons.types import Point
import threading
import math
from opentrons import types
from opentrons import protocol_api
import numpy as np

metadata = {
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>',
    'protocolName': 'Thermo MagMax RNA Extraction: Cells Multi-Channel',
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.20",
}
"""
Slot A1: Tips 200
Slot A2: Tips 200
Slot A3: Temperature module (gen2) with 96 well PCR block and Armadillo 96 well PCR Plate
** Plate gets 55 ul per well in each well of the entire plate
Slot B1: Tips 200
Slot B2: Tips 200
Slot B3: Nest 1 Well Reservoir
Slot C1: Magblock
Slot C2: 
Slot C3: 
Slot D1: H-S with Nest 96 Well Deepwell and DW Adapter
Slot D2: Nest 12 well 15 ml Reservoir
Slot D3: Trash

Reservoir 1:
Well 1 - 8120 ul
Well 2 - 6400 ul
Well 3-7 - 8550 ul
"""

whichwash = 1
sample_max = 48
tip = 0
drop_count = 0
waste_vol = 0


# Start protocol
def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_csv_file(
        variable_name="parameters_csv",
        display_name="Parameters CSV File",
        description="CSV file containing parameters for this protocol",
    )
    
def run(ctx:protocol_api.ProtocolContext):
    """
    Here is where you can change the locations of your labware and modules
    (note that this is the recommended configuration)
    """
    trash_chute = False
    USE_GRIPPER = True
    dry_run = False
    inc_lysis = True
    mount = 'left'
    res_type = "nest_12_reservoir_15ml"
    temp_mod = True
    TIP_TRASH = False
    num_samples = 48
    wash_vol= 150
    sample_vol = 50
    lysis_vol = 140
    stop_vol = 100
    elution_vol = dnase_vol = 50

    csv_params = ctx.params.parameters_csv.parse_as_csv()
    heater_shaker_speed = int(csv_params[1][0])
    temp_mod_timeout = int(csv_params[1][1])
    dot_bottom = csv_params[1][2]
    # heater_shaker_speed = ctx.params.heater_shaker_speed
    # temp_mod_timeout = ctx.params.temp_mod_timeout
    # dot_bottom = ctx.params.dot_bottom
    try:
        [res_type,temp_mod,trash_chute,USE_GRIPPER, dry_run,inc_lysis,mount,num_samples,wash_vol,lysis_vol,sample_vol,stop_vol,dnase_vol,elution_vol] = get_values(  # noqa: F821
        'res_type','temp_mod','trash_chute','USE_GRIPPER','dry_run','inc_lysis','mount','num_samples','wash_vol','lysis_vol','sample_vol','stop_vol','dnase_vol','elution_vol')

    except (NameError):
        pass
    
    #Protocol Parameters
    deepwell_type = "nest_96_wellplate_2ml_deep"
    
    if not dry_run:
        settling_time = 2
    else:
        settling_time = 0.25
    bead_vol = 20
    starting_vol= sample_vol+lysis_vol
    if trash_chute:
        trash = ctx.load_waste_chute()
    else:
        trash = ctx.load_trash_bin('A3')
        
    h_s = ctx.load_module('heaterShakerModuleV1','D1')
    h_s_adapter = h_s.load_adapter('opentrons_96_deep_well_adapter')
    sample_plate = h_s_adapter.load_labware(deepwell_type,'Sample Plate')
    h_s.close_labware_latch()
    
    if temp_mod:
        temp = ctx.load_module('temperature module gen2','D3')
        temp_block = temp.load_adapter('opentrons_96_well_aluminum_block')
        elutionplate = temp_block.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt','Elution Plate')
        if not dry_run:
            def set_temperature_with_timeout(temp_block, timeout):
                def set_temperature():
                    temp_block.set_temperature(4)

                # Create a thread to run the set_temperature function
                thread = threading.Thread(target=set_temperature)
                thread.start()
                thread.join(timeout)

                if thread.is_alive():
                    raise RuntimeError(f"Temperature module timeout. Took longer than {timeout} seconds to reach 4 C. Protocol terminated.")
            try:
                set_temperature_with_timeout(temp, temp_mod_timeout)
            except RuntimeError as e:
                ctx.comment(str(e))
                raise
    else:
        elutionplate = ctx.load_labware('opentrons_96_wellplate_200ul_pcr_full_skirt','A3','Elution Plate')

    magblock = ctx.load_module('magneticBlockV1','C1')
    waste = ctx.load_labware('nest_1_reservoir_195ml', 'B3','Liquid Waste').wells()[0].top()
    res1 = ctx.load_labware(res_type, 'D2', 'reagent reservoir 1')
    num_cols = math.ceil(num_samples/8)
    
    #Load tips and combine all similar boxes
    tips200 = ctx.load_labware('opentrons_flex_96_tiprack_200ul', 'A1','Tips 1')
    tips201 = ctx.load_labware('opentrons_flex_96_tiprack_200ul', 'A2','Tips 2')
    tips202 = ctx.load_labware('opentrons_flex_96_tiprack_200ul', 'B1','Tips 3')
    tips203 = ctx.load_labware('opentrons_flex_96_tiprack_200ul', 'B2','Tips 4')
    tips = [*tips200.wells()[num_samples:96],*tips201.wells(),*tips202.wells(),*tips203.wells()]
    tips_sn = tips200.wells()[:num_samples]

    # load P1000M pipette
    m1000 = ctx.load_instrument('flex_8channel_1000', mount)

    # Load Liquid Locations in Reservoir
    elution_solution = elutionplate.rows()[0][:num_cols]
    dnase1 = elutionplate.rows()[0][num_cols:2*num_cols]
    lysis_ = res1.wells()[0]
    stopreaction = res1.wells()[1]
    wash1 = res1.wells()[2]
    wash2 = res1.wells()[3]
    wash3 = res1.wells()[4]
    wash4 = res1.wells()[5]
    wash5 = res1.wells()[6] 

    """
    Here is where you can define the locations of your reagents.
    """
    samples_m = sample_plate.rows()[0][:num_cols] #20ul beads each well
    cells_m = sample_plate.rows()[0][num_cols:2*num_cols]
    elution_samples_m = elutionplate.rows()[0][:num_cols]
    #Do the same for color mapping
    beads_ = sample_plate.wells()[:(8*num_cols)]
    cells_ = sample_plate.wells()[(8*num_cols):(16*num_cols)]
    elution_samps = elutionplate.wells()[:(8*num_cols)]
    dnase1_ = elutionplate.wells()[(8*num_cols):(16*num_cols)]

    colors = ['#008000','#A52A2A','#00FFFF','#0000FF','#800080',\
    '#ADD8E6','#FF0000','#FFFF00','#FF00FF','#00008B','#7FFFD4',\
    '#FFC0CB','#FFA500','#00FF00','#C0C0C0']

    locations = [lysis_,wash1,wash2,wash3,wash4,wash5,stopreaction]
    vols = [lysis_vol,wash_vol,wash_vol,wash_vol,wash_vol,wash_vol,stop_vol]
    liquids = ['Lysis','Wash 1','Wash 2','Wash 3','Wash 4','Wash 5','Stop']

    dnase = ctx.define_liquid(name='DNAse',description='DNAse',display_color='#C0C0C0')
    eluate = ctx.define_liquid(name='Elution Buffer',description='Elution Buffer',display_color='#00FF00')
    bead = ctx.define_liquid(name='Beads',description='Beads',display_color='#FFA500')
    sample = ctx.define_liquid(name='Sample',description='Cell Pellet',display_color='#FFC0CB')

    #Add liquids to non-reservoir labware
    for i in beads_:
        i.load_liquid(liquid=bead,volume=bead_vol)
    for i in cells_:
        i.load_liquid(liquid=sample,volume=0)
    for i in dnase1_:
        i.load_liquid(liquid=dnase,volume=dnase_vol)
    for i in elution_samps:
        i.load_liquid(liquid=eluate,volume=elution_vol)

    delete = len(colors)-len(liquids)

    if delete>=1:
        for i in range(delete):
            colors.pop(-1)

    def liquids_(liq,location,color,vol):
        sampnum = 8*(math.ceil(num_samples/8))
        """
        Takes an individual liquid at a time and adds the color to the well
        in the description.
        """
        #Volume Calculation
        extra_samples = math.ceil(1500/vol)
        
        #Defining and assigning liquids to wells
        # if isinstance(location,list):
        #     limit = sample_max/len(location) #Calculates samples/ res well
        #     iterations = math.ceil(sampnum/limit)
        #     left = sampnum - limit
        #     while left>limit:
        #         left = left - limit
        #     if left > 0:
        #         last_iteration_samp_num = left
        #     elif left < 0:
        #         last_iteration_samp_num = sampnum
        #     else:
        #         last_iteration_samp_num = limit

        #     samples_per_well = []

        #     for i in range(iterations):
        #         #append the left over on the last iteration
        #         if i == (iterations-1):
        #             samples_per_well.append(last_iteration_samp_num)
        #         else:
        #             samples_per_well.append(limit)

        #     liq = ctx.define_liquid(name=str(liq),description=str(liq),display_color=color)
        #     for sample, well in zip(samples_per_well,location[:len(samples_per_well)]):
        #         v = vol*(sample+extra_samples)
        #         well.load_liquid(liquid=liq,volume=v)
        #else:
        v = vol*(sampnum+extra_samples)
        liq = ctx.define_liquid(name=str(liq),description=str(liq),display_color=color)
        location.load_liquid(liquid=liq,volume=v)

    for x,(ll,l,c,v) in enumerate(zip(liquids,locations,colors,vols)):
        liquids_(ll,l,c,v)

    # for x in range(len(locations)):
    #     ctx.comment("Location:" + str(locations[x]))
    #     ctx.comment("Liquid:" + str(liquids[x]))
    #     ctx.comment("Color:" + str(colors[x]))
    #     ctx.comment("Volume:" + str(vols[x]))
    
    m1000.flow_rate.aspirate = 50
    m1000.flow_rate.dispense = 150
    m1000.flow_rate.blow_out = 300

    def tiptrack(pip, tipbox):
        global tip
        global drop_count
        pip.pick_up_tip(tipbox[int(tip)])
        tip = tip + 8
        drop_count = drop_count + 8
        if drop_count >= 250:
            drop_count = 0
            if TIP_TRASH == True:
                ctx.pause("Please empty the waste bin of all the tips before continuing.")
    def blink():
        for i in range(3):
            ctx.set_rail_lights(True)
            ctx.delay(minutes=0.01666667)
            ctx.set_rail_lights(False)
            ctx.delay(minutes=0.01666667)

    def remove_supernatant(vol):
        ctx.comment("-----Removing Supernatant-----")
        m1000.flow_rate.aspirate = 30
        num_trans = math.ceil(vol/180)
        vol_per_trans = vol/num_trans

        def _waste_track(vol):
            global waste_vol 
            waste_vol = waste_vol + (vol*8)
            if waste_vol >= 185000:
                m1000.home()
                blink()
                ctx.pause('Please empty liquid waste before resuming.')
                waste_vol = 0

        for i, m in enumerate(samples_m):
            m1000.pick_up_tip(tips_sn[8*i])
            loc = m.bottom(dot_bottom)
            for _ in range(num_trans):
                if m1000.current_volume > 0:
                    # void air gap if necessary
                    m1000.dispense(m1000.current_volume, m.top())
                m1000.move_to(m.center())
                m1000.transfer(vol_per_trans, loc, waste, new_tip='never',air_gap=20)
                m1000.blow_out(waste)
                m1000.air_gap(20)
            m1000.drop_tip(tips_sn[8*i]) if TIP_TRASH == True else m1000.return_tip()
        m1000.flow_rate.aspirate = 300
        #Move Plate From Magnet to H-S
        h_s.open_labware_latch()
        ctx.move_labware(
            sample_plate,
            h_s_adapter,
            use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

    def bead_mixing(well, pip, mvol, reps=8):
        """
        'mixing' will mix liquid that contains beads. This will be done by
        aspirating from the bottom of the well and dispensing from the top as to
        mix the beads with the other liquids as much as possible. Aspiration and
        dispensing will also be reversed for a short to to ensure maximal mixing.
        param well: The current well that the mixing will occur in.
        param pip: The pipet that is currently attached/ being used.
        param mvol: The volume that is transferred before the mixing steps.
        param reps: The number of mix repetitions that should occur. Note~
        During each mix rep, there are 2 cycles of aspirating from bottom,
        dispensing at the top and 2 cycles of aspirating from middle,
        dispensing at the bottom
        """
        center = well.top().move(types.Point(x=0,y=0,z=5))
        aspbot = well.bottom().move(types.Point(x=0,y=0,z=1))
        asptop = well.bottom().move(types.Point(x=2,y=-2,z=1))
        disbot = well.bottom().move(types.Point(x=-2,y=1.5,z=2))
        distop = well.bottom().move(types.Point(x=0,y=0,z=6))

        if mvol > 1000:
            mvol = 1000

        vol = mvol * .9

        pip.flow_rate.aspirate = 500
        pip.flow_rate.dispense = 500

        pip.move_to(center)
        for _ in range(reps):
            pip.aspirate(vol,aspbot)
            pip.dispense(vol,distop)
            pip.aspirate(vol,asptop)
            pip.dispense(vol,disbot)
            if _ == reps-1:
                pip.flow_rate.aspirate = 100
                pip.flow_rate.dispense = 75
                pip.aspirate(vol,aspbot)
                pip.dispense(vol,aspbot)

        pip.flow_rate.aspirate = 300
        pip.flow_rate.dispense = 300

    def mixing(well, pip, mvol, reps=8):
        """
        'mixing' will mix liquid that contains beads. This will be done by
        aspirating from the bottom of the well and dispensing from the top as to
        mix the beads with the other liquids as much as possible. Aspiration and
        dispensing will also be reversed for a short to to ensure maximal mixing.
        param well: The current well that the mixing will occur in.
        param pip: The pipet that is currently attached/ being used.
        param mvol: The volume that is transferred before the mixing steps.
        param reps: The number of mix repetitions that should occur. Note~
        During each mix rep, there are 2 cycles of aspirating from bottom,
        dispensing at the top and 2 cycles of aspirating from middle,
        dispensing at the bottom
        """
        center = well.top(5)
        asp = well.bottom(dot_bottom)
        disp = well.top(-8)

        if mvol > 1000:
            mvol = 1000

        vol = mvol * .9

        pip.flow_rate.aspirate = 500
        pip.flow_rate.dispense = 500

        pip.move_to(center)
        for _ in range(reps):
            pip.aspirate(vol,asp)
            pip.dispense(vol,disp)
            pip.aspirate(vol,asp)
            pip.dispense(vol,disp)
            if _ == reps-1:
                pip.flow_rate.aspirate = 100
                pip.flow_rate.dispense = 75
                pip.aspirate(vol,asp)
                pip.dispense(vol,asp)

        pip.flow_rate.aspirate = 300
        pip.flow_rate.dispense = 300

    def lysis(vol, source):
        ctx.comment("-----Beginning lysis steps-----")
        num_transfers = math.ceil(vol/180)
        tiptrack(m1000, tips)
        for i in range(num_cols):
            src = source
            tvol = vol/num_transfers
            for t in range(num_transfers):
                m1000.require_liquid_presence(src)
                m1000.aspirate(tvol,src.bottom(1))
                m1000.dispense(m1000.current_volume,cells_m[i].top(-3))
                
        #mix after adding all reagent to wells with cells
        for i in range(num_cols):
            if i != 0:
                tiptrack(m1000,tips)
            for x in range(8 if not dry_run else 1):
                m1000.aspirate(tvol*.75,cells_m[i].bottom(dot_bottom))
                m1000.dispense(tvol*.75,cells_m[i].bottom(8))
                if x == 3:
                    ctx.delay(minutes=0.0167)
                    m1000.blow_out(cells_m[i].bottom(1))
            m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()

        h_s.set_and_wait_for_shake_speed(heater_shaker_speed*1.1)
        ctx.delay(minutes=1 if not dry_run else 0.25,msg='Please allow 1 minute incubation for cells to lyse')
        h_s.deactivate_shaker()

    def bind():
        """
        `bind` will perform magnetic bead binding on each sample in the
        deepwell plate. Each channel of binding beads will be mixed before
        transfer, and the samples will be mixed with the binding beads after
        the transfer. The magnetic deck activates after the addition to all
        samples, and the supernatant is removed after bead binding.
        :param vol (float): The amount of volume to aspirate from the elution
                            buffer source and dispense to each well containing
                            beads.
        :param park (boolean): Whether to save sample-corresponding tips
                               between adding elution buffer and transferring
                               supernatant to the final clean elutions PCR
                               plate.
        """
        ctx.comment("-----Beginning bind steps-----")
        for i, well in enumerate(samples_m):
            #Transfer cells+lysis/bind to wells with beads
            tiptrack(m1000,tips)
            m1000.aspirate(185,cells_m[i].bottom(dot_bottom))
            m1000.air_gap(10)
            m1000.dispense(m1000.current_volume,well.bottom(8))
            #Mix after transfer
            bead_mixing(well,m1000,130, reps=5 if not dry_run else 1)
            m1000.air_gap(10)
            m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()

        h_s.set_and_wait_for_shake_speed(heater_shaker_speed)
        ctx.delay(minutes=5 if not dry_run else 0.25,msg='Please allow 5 minute incubation for beads to bind to DNA')
        h_s.deactivate_shaker()

        #Transfer from H-S plate to Magdeck plate
        h_s.open_labware_latch()
        ctx.move_labware(
            sample_plate,
            magblock,
            use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for bindi in np.arange(settling_time,0,-0.5): #Settling time delay with countdown timer
            ctx.delay(minutes=0.5, msg='There are ' + str(bindi) + ' minutes left in the incubation.')

        # remove initial supernatant
        remove_supernatant(180)

    def wash(vol, source):

        global whichwash #Defines which wash the protocol is on to log on the app

        if source == wash1:
            whichwash = 1
        if source == wash2:
            whichwash = 2
        if source == wash3:
            whichwash = 3
        if source == wash4:
            whichwash = 4

        ctx.comment("-----Now starting Wash #" + str(whichwash) + "-----")

        tiptrack(m1000,tips)
        num_trans = math.ceil(vol/180)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(samples_m):
            src = source
            m1000.detect_liquid_presence = True
            for n in range(num_trans):
                m1000.aspirate(vol_per_trans, src)
                m1000.air_gap(10)
                m1000.dispense(m1000.current_volume, m.top(-2))
                ctx.delay(seconds=2)
                m1000.blow_out(m.top(-2))
            m1000.detect_liquid_presence = False
            m1000.air_gap(10)
        m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()

        #Shake for 5 minutes to mix wash with beads
        h_s.set_and_wait_for_shake_speed(heater_shaker_speed)
        ctx.delay(minutes=5 if not dry_run else 0.25,msg='Please allow 5 minute incubation for beads to mix in wash buffer')
        h_s.deactivate_shaker()

        #Transfer from H-S plate to Magdeck plate
        h_s.open_labware_latch()
        ctx.move_labware(
            sample_plate,
            magblock,
            use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for washi in np.arange(settling_time,0,-0.5): #settling time timer for washes
            ctx.delay(minutes=0.5, msg='There are ' + str(washi) + ' minutes left in wash ' + str(whichwash) + ' incubation.')

        remove_supernatant(vol)

    def dnase(vol, source):
        ctx.comment("-----DNAseI Steps Beginning-----")
        num_trans = math.ceil(vol/180)
        vol_per_trans = vol/num_trans
        tiptrack(m1000, tips)
        for i, m in enumerate(samples_m):
            src = source[i]
            m1000.flow_rate.aspirate = 10
            for n in range(num_trans):
                if m1000.current_volume > 0:
                    m1000.dispense(m1000.current_volume, src.top())
                m1000.aspirate(vol_per_trans, src.bottom(dot_bottom))
                m1000.dispense(vol_per_trans, m.top(-3))
            m1000.blow_out(m.top(-3))
            m1000.air_gap(20)
        
        m1000.flow_rate.aspirate = 300

        #Is this mixing needed? \/\/\/
        for i in range(num_cols):
            if i != 0:
                tiptrack(m1000,tips)
            mixing(samples_m[i], m1000, 45, reps=5 if not dry_run else 1)
            m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()

        #Shake for 10 minutes to mix DNAseI
        h_s.set_and_wait_for_shake_speed(heater_shaker_speed)
        ctx.delay(minutes=10 if not dry_run else 0.25,msg='Please allow 10 minute incubation for DNAse1 to work')
        h_s.deactivate_shaker()

    def stop_reaction(vol, source):
        ctx.comment("-----Adding Stop Solution-----")
        tiptrack(m1000, tips)
        num_trans = math.ceil(vol/180)
        vol_per_trans = vol/num_trans
        for i, m in enumerate(samples_m):    
            src = source
            for n in range(num_trans):
                if m1000.current_volume > 0:
                    m1000.dispense(m1000.current_volume, src.top())
                m1000.transfer(vol_per_trans, src, m.top(), air_gap=20,new_tip='never')
            m1000.blow_out(m.top(-3))
            m1000.air_gap(20)
        
        m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()
            
        #Shake for 3 minutes to mix wash with beads
        h_s.set_and_wait_for_shake_speed(heater_shaker_speed)
        ctx.delay(minutes=3 if not dry_run else 0.25,msg='Please allow 3 minute incubation to inactivate DNAse1')
        h_s.deactivate_shaker()

        #Transfer from H-S plate to Magdeck plate
        h_s.open_labware_latch()
        ctx.move_labware(
            sample_plate,
            magblock,
            use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for stop in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5,msg='There are ' + str(stop) + ' minutes left in this incubation.')

        remove_supernatant(vol+50)

    def elute(vol):
        ctx.comment("-----Elution Beginning-----")
        tiptrack(m1000,tips)
        m1000.flow_rate.aspirate = 10
        for i, m in enumerate(samples_m):
            loc = m.top(-2)
            m1000.aspirate(vol, elution_solution[i])
            m1000.air_gap(10)
            m1000.dispense(m1000.current_volume, loc)
            m1000.blow_out(m.top(-3))
            m1000.air_gap(10)
           
        m1000.flow_rate.aspirate = 300    

        #Is this mixing needed? \/\/\/
        for i in range(num_cols):
            if i != 0:
                tiptrack(m1000, tips)
            for mixes in range(10):
                m1000.aspirate(elution_vol-10, samples_m[i])
                m1000.dispense(elution_vol-10, samples_m[i].bottom(10))
                if mixes == 9:
                    m1000.flow_rate.dispense = 20
                    m1000.aspirate(elution_vol-10, samples_m[i])
                    m1000.dispense(elution_vol-10, samples_m[i].bottom(10))
                    m1000.flow_rate.dispense = 300
            m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()

        #Shake for 3 minutes to mix wash with beads
        h_s.set_and_wait_for_shake_speed(heater_shaker_speed)
        ctx.delay(minutes=3 if not dry_run else 0.25,msg='Please allow 3 minute incubation to elute RNA from beads')
        h_s.deactivate_shaker()
        
        #Transfer from H-S plate to Magdeck plate
        h_s.open_labware_latch()
        ctx.move_labware(
            sample_plate,
            magblock,
            use_gripper=USE_GRIPPER)
        h_s.close_labware_latch()

        for elutei in np.arange(settling_time,0,-0.5):
            ctx.delay(minutes=0.5, msg='Incubating on MagDeck for ' + str(elutei) + ' more minutes.')

        ctx.comment("-----Trasnferring Sample to Elution Plate-----")
        for i, (m, e) in enumerate(zip(samples_m, elution_samples_m)):
            tiptrack(m1000,tips)
            loc = m.bottom(dot_bottom)
            m1000.transfer(vol, loc, e.bottom(5), air_gap=20, new_tip='never')
            m1000.blow_out(e.top(-2))
            m1000.air_gap(20)
            m1000.drop_tip() if TIP_TRASH == True else m1000.return_tip()

    """
    Here is where you can call the methods defined above to fit your specific
    protocol. The normal sequence is:
    """
    if inc_lysis:
        lysis(lysis_vol,lysis_)
    bind()
    wash(wash_vol, wash1)
    wash(wash_vol, wash2)
    #dnase1 treatment
    dnase(dnase_vol, dnase1)
    stop_reaction(stop_vol, stopreaction)
    #Resume washes
    wash(wash_vol, wash3)
    wash(wash_vol, wash4)
    wash(wash_vol, wash5)
    if not dry_run:
        drybeads = 2 #Number of minutes you want to dry for
    else:
        drybeads = 0.25
    for beaddry in np.arange(drybeads,0,-0.5):
        ctx.delay(minutes=0.5, msg='There are ' + str(beaddry) + ' minutes left in the drying step.')
    elute(elution_vol)