from opentrons import protocol_api
from opentrons import types
import os
import subprocess

ALL_LOGS = "/data/logs/all_logs.log"
CAN_MON = "/data/logs/can_mon.log"

metadata = {
    'protocolName': 'Testing Changes Protocol',
    'author': 'Opentrons <protocols@opentrons.com>',
    'source': 'Protocol Library',
    'apiLevel': '2.15'
}

requirements = {
    "robotType" : "OT-3",
    "apiLevel": "2.15",
}

DRYRUN = 'YES'
USE_GRIPPER = True

def run(protocol: protocol_api.ProtocolContext):
    
    if not protocol.is_simulating():
        if os.path.exists(ALL_LOGS):
            os.remove(ALL_LOGS)
        all_logs = open(ALL_LOGS, "w")
        if os.path.exists(CAN_MON):
            os.remove(CAN_MON)
        can_mon = open(CAN_MON, "w")
        subprocess.Popen(["journalctl", "-f"], stdout=all_logs)
        subprocess.Popen(["python3", "-m", "opentrons_hardware.scripts.can_mon"], stdout=can_mon)
    
    global DRYRUN

    def grip_offset(action, item, slot=None):
        """Grip offset."""
        from opentrons.types import Point

        # EDIT these values
        # NOTE: we are still testing to determine our software's defaults
        #       but we also expect users will want to edit these
        _pick_up_offsets = {
            "deck": Point(),
            "mag-plate": Point(),
            "heater-shaker": Point(z=1.0),
            "temp-module": Point(),
            "thermo-cycler": Point(),
        }
        # EDIT these values
        # NOTE: we are still testing to determine our software's defaults
        #       but we also expect users will want to edit these
        _drop_offsets = {
            "deck": Point(),
            "mag-plate": Point(z=0.5),
            "heater-shaker": Point(),
            "temp-module": Point(),
            "thermo-cycler": Point(),
        }
        # do NOT edit these values
        # NOTE: these values will eventually be in our software
        #       and will not need to be inside a protocol
        _hw_offsets = {
            "deck": Point(),
            "mag-plate": Point(z=2.5),
            "heater-shaker-right": Point(z=2.5),
            "heater-shaker-left": Point(z=2.5),
            "temp-module": Point(z=5.0),
            "thermo-cycler": Point(z=2.5),
        }
        # make sure arguments are correct
        action_options = ["pick-up", "drop"]
        item_options = list(_hw_offsets.keys())
        item_options.remove("heater-shaker-left")
        item_options.remove("heater-shaker-right")
        item_options.append("heater-shaker")
        if action not in action_options:
            raise ValueError(
                f'"{action}" not recognized, available options: {action_options}'
            )
        if item not in item_options:
            raise ValueError(
                f'"{item}" not recognized, available options: {item_options}'
            )
        if item == "heater-shaker":
            assert slot, 'argument slot= is required when using "heater-shaker"'
            if slot in [1, 4, 7, 10]:
                side = "left"
            elif slot in [3, 6, 9, 12]:
                side = "right"
            else:
                raise ValueError("heater shaker must be on either left or right side")
            hw_offset = _hw_offsets[f"{item}-{side}"]
        else:
            hw_offset = _hw_offsets[item]
        if action == "pick-up":
            offset = hw_offset + _pick_up_offsets[item]
        else:
            offset = hw_offset + _drop_offsets[item]

        # convert from Point() to dict()
        return {"x": offset.x, "y": offset.y, "z": offset.z}

    #tiprack_200 = protocol.load_labware('opentrons_ot3_96_tiprack_200ul', 'D2')
    tiprack_50 = protocol.load_labware('opentrons_ot3_96_tiprack_50ul', 'C2')

    heat_shake = protocol.load_module('heaterShakerModuleV1', 'D1')
    plate = heat_shake.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    temp_deck = protocol.load_module('temperature module gen2', 'D3')
    thermocycler = protocol.load_module('thermocycler module gen2')
    # pipette
    p50 = protocol.load_instrument("p50_single_gen3", "left", tip_racks=[tiprack_50])

    for i in range(3):

        heat_shake.open_labware_latch()
        thermocycler.open_lid()
        #protocol.pause("Ready!")
        heat_shake.close_labware_latch()

        p50.pick_up_tip()
        p50.move_to(plate['A1'].top())
        p50.return_tip()

        heat_shake.open_labware_latch()
        protocol.move_labware(
            labware = plate,
            new_location = temp_deck,
            use_gripper = USE_GRIPPER,
            use_pick_up_location_lpc_offset=True,
            use_drop_location_lpc_offset=True,
            pick_up_offset=grip_offset("pick-up", "heater-shaker",1),
            drop_offset=grip_offset("drop", "temp-module"),
        )
        heat_shake.close_labware_latch()

        p50.pick_up_tip()
        p50.move_to(plate['A1'].top())
        p50.return_tip()

        thermocycler.open_lid()
        protocol.move_labware(
            labware = plate,
            new_location = thermocycler,
            use_gripper = USE_GRIPPER,
            use_pick_up_location_lpc_offset=True,
            use_drop_location_lpc_offset=True,
            pick_up_offset=grip_offset("pick-up", "temp-module"),
            drop_offset=grip_offset("drop", "thermo-cycler"),
        )

        p50.pick_up_tip()
        p50.move_to(plate['A1'].top())
        p50.return_tip()

        thermocycler.close_lid()
        #protocol.delay(seconds=20)
        thermocycler.open_lid()

        heat_shake.open_labware_latch()
        protocol.move_labware(
            labware = plate,
            new_location = heat_shake,
            use_gripper = USE_GRIPPER,
            use_pick_up_location_lpc_offset=True,
            use_drop_location_lpc_offset=True,
            pick_up_offset=grip_offset("pick-up", "thermo-cycler"),
            drop_offset=grip_offset("drop", "heater-shaker", 1),
        )








