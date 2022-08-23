import subprocess

from opentrons import protocol_api, types

metadata = {"apiLevel": "2.9"}
AUDIO_FILE_PATH = "/etc/audio/speaker-test.mp3"


def run_quiet_process(command):
    subprocess.check_output("{} &> /dev/null".format(command), shell=True)


def test_speaker():
    print("Speaker")
    print("Next\t--> CTRL-C")
    try:
        run_quiet_process("mpg123 {}".format(AUDIO_FILE_PATH))
    except KeyboardInterrupt:
        pass
        print()


def run(protocol: protocol_api.ProtocolContext):
    tr2 = protocol.load_labware("opentrons_96_tiprack_300ul", "1")
    p300 = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tr2])
    p300.pick_up_tip()
    p300.drop_tip()
    test_speaker()
