from opentrons import protocol_api

metadata = {
    'protocolName': 'Drying out Modules Protocol',
    'author': 'Rhyann Clarke: rhyann.clarke@opentrons.com',
    'description': 'Use parameters to select which module to heat up.'
}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.19",
}

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_str(
            variable_name="module_type",
            display_name="Module Type",
            description="What module to use",
            choices=[
                {"display_name": "Thermocycler", "value": "thermocycler module gen2"},
                {"display_name": "Temperature Module", "value": "temperature module gen2"},
                
            ],
            default="thermocycler module gen2",
        )
    parameters.add_str(
            variable_name="module_location",
            display_name="Module Location",
            description="Slot module is in.",
            choices=[
                {"display_name": "A1", "value": "A1"},
                {"display_name": "A2", "value": "A2"},
                {"display_name": "A3", "value": "A3"},
                {"display_name": "B1", "value": "B1"},
                {"display_name": "B2", "value": "B2"},
                {"display_name": "B3", "value": "A3"},
                {"display_name": "C1", "value": "C1"},
                {"display_name": "C2", "value": "C2"},
                {"display_name": "C3", "value": "C3"},
                {"display_name": "D1", "value": "D1"},
                {"display_name": "D2", "value": "D2"},
                {"display_name": "D3", "value": "D3"},
                
            ],
            default="A1",
        )
    parameters.add_float(
        variable_name = "heat_up_time_min",
        display_name = "Heat up Time (min)",
        description = "Duration for module to stay at 40 C",
        default = 30,
        choices=[
            {"display_name": "10", "value": 10},
            {"display_name": "20", "value": 20},
            {"display_name": "30", "value": 30},
            {"display_name": "40", "value": 40},
            {"display_name": "50", "value": 50},
            {"display_name": "60", "value": 60},
        ]
    )

def run(protocol: protocol_api.ProtocolContext):
    module_type = protocol.params.module_type
    module_location = protocol.params.module_location
    heat_up_time_min = protocol.params.heat_up_time_min
    protocol.comment(f"Running: {module_type} at 40 C for {heat_up_time_min}")
    
    
    if module_type == "thermocycler module gen2":
        module = protocol.load_module(module_type)
        module.set_lid_temperature(105)
        module.set_block_temperature(40, hold_time_minutes = heat_up_time_min)
    else:
        module = protocol.load_module(module_type, module_location)
        module.set_temperature(40)
        protocol.delay(minutes = heat_up_time_min)
        
    
    