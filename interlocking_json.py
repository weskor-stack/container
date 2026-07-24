import json
import conexion

def interlocking(parent_serial_number, parent_part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    program_id = configurador[4]

    unit_information.append({
            "name": "Program name + version ",
            "value": program_id
        })

    unit_information.append({
        "name": "Machine_ID",
        "value": machine_id
    })

    interlocking = {
        "serial": parent_serial_number,
        "product": parent_part_number,
        "station": machine_id,
        "operator": operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking, indent=4))
    return interlocking

# interlocking("P1472635-61-G:SE4A22172000000","LFTM1755080-01-F")

