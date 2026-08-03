import json
import conexion

def new_container(parent_serial_number):
    unit_information = []
    part_number = conexion.obtener_parte2(parent_serial_number)
    part_number = part_number[2]
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    program_id = configurador[4]
    client_id = configurador[6]
    password = configurador[7]
    qty_pcba = configurador[14]


    container = {
        "version":"1.0",
        "keep_alive":False,
        "refresh_unit":True,
        "source":{
            "workstation":{
                "station":process_name,
                "type":"PROCESS"
            },
            "client_id":client_id,
            "employee":operator,
            "password":password
        },
        "transactions":[
            {
                "unit":{
                    "unit_id":""
                },
                "commands":[
                    {
                        "name":"CreateContainer",
                        "c_level":qty_pcba,
                        "container_part_number":part_number
                    }
                ]
            }
        ]        
    }
    # print(json.dumps(container, indent=4))
    return container


def add_component(serial_number,serial_container):
    part_number = conexion.obtener_parte2(serial_number)
    part_number = part_number[2]
    configurador = conexion.configurador()
    get_container = conexion.get_container(serial_number)
    process_name = configurador[1]
    operator = configurador[2]
    client_id = configurador[6]
    password = configurador[7]

    if get_container == None:
        return "FAILED",f"No container found for serial number: {serial_number}",""
    
    container = {
        "version":"1.0",
        "keep_alive":False,
        "refresh_unit":True,
        "source":{
            "workstation":{
                "station":process_name,
                "type":"PROCESS"
            },
            "client_id":client_id,
            "employee":operator,
            "password":password
        },
        "transactions":[
            {
                "unit":{
                    "unit_id":get_container[0]
                },
                "commands":[
                    {
                        "name":"AddUnitToContainer",
                       "unit_serial_number":serial_container
                    }
                ]
            }
        ]        
    }
    # print(json.dumps(container, indent=4))
    return container


def print_label(serial_number):
    part_number = conexion.obtener_parte2(serial_number)
    part_number = part_number[2]
    configurador = conexion.configurador()
    get_container = conexion.get_container(serial_number)
    process_name = configurador[1]
    operator = configurador[2]
    client_id = configurador[6]
    password = configurador[7]
    print_macro = configurador[10]

    if get_container == None:
        return "FAILED",f"No container found for serial number: {serial_number}",""
    
    container = {
        "version":"1.0",
        "keep_alive":False,
        "refresh_unit":True,
        "source":{
            "workstation":{
                "station":process_name,
                "type":"PROCESS"
            },
            "client_id":client_id,
            "employee":operator,
            "password":password
        },
        "transactions":[
            {
                "unit":{
                    "unit_id":get_container[0]
                },
                "commands":[
                    {
                        "name":print_macro
                    }
                ]
            }
        ]        
    }
    # print(json.dumps(container, indent=4))
    return container

# print_label("P1472635-61-G:SE4A22172000000")
# add_component("P1472635-61-G:SE4A22172000000","TEST-12635565465465465")
# new_container("P1472635-61-G:SE4A22172000000")

