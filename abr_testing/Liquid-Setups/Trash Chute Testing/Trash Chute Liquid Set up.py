from opentrons import protocol_api

metadata = {
    'protocolName': 'Trash Chute Liquid Set Up - Deep Well Plates',
    'author': 'Rhyann clarke <rhyann.clarke@opentrons.com>',
    'source': 'Protocol Library',
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.15",
}



def run(protocol: protocol_api.ProtocolContext):
    #PLATE = 'armadillo_96_wellplate_200ul_pcr_full_skirt'
    # vol = 95 
    PLATE = 'nest_96_wellplate_2ml_deep' 
    vol = 1900
    
    # Load Labware
    master_reservoir    = protocol.load_labware('axygen_1_reservoir_90ml', 'C2')
    tiprack_1000        = protocol.load_labware(load_name='opentrons_flex_96_tiprack_1000ul', location='D1') # Tip Rack
    
    plate_1        = protocol.load_labware(PLATE,'B3')  
    plate_2        = protocol.load_labware(PLATE,'C3') 
    plate_3        = protocol.load_labware(PLATE,'D2')
    plate_4        = protocol.load_labware(PLATE,'D3')
    
        
    # Load Pipette
    p1000               = protocol.load_instrument(instrument_name='flex_8channel_1000', mount='left', tip_racks=[tiprack_1000]) # Pipette
    plates              = [plate_1, plate_2, plate_3, plate_4]

    # Fill up plates
    for i in plates:
        p1000.distribute([vol, vol, vol, vol, vol, vol, vol, vol, vol, vol, vol, vol], source = master_reservoir['A1'].bottom(z=0.5), dest = [i['A1'], i['A2'], i['A3'], i['A4'], i['A5'], i['A6'], i['A7'], i['A8'], i['A9'], i['A10'], i['A11'], i['A12']], new_tip = "once")