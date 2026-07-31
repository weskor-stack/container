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

# new_container("P1472635-61-G:SE4A22172000000")

