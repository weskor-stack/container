import json
import conexion
import rfc3339
from datetime import datetime, timezone
import pendulum
from zoneinfo import ZoneInfo


def traceability_container(serial_padre, resultado, tipo, error_code, comentario):
    configurador = conexion.configurador()
    
    parte = conexion.obtener_parte2(serial_padre)

    if configurador and configurador != "FAILED":
        machine_id = configurador[0]
        process_name = configurador[1]
        operator_id = configurador[2]
        program_version = configurador[4]
        password = configurador[7]
    else:
        machine_id = "AMC-GENLD97"
        operator_id = "TST99999"
        process_name = "Container"
        program_version = "default_program"
        password = ""

    now = datetime.now(ZoneInfo("America/Mexico_City"))
    now_utc = now.strftime("%m/%d/%Y %I:%M:%S %p")
    fecha = str(parte[4])
    # Convertir la cadena a datetime
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

    # Dar el formato deseado
    fecha_formateada = fecha_dt.strftime("%m/%d/%Y %I:%M:%S %p")
    
    program_version = str(program_version).strip() if program_version else "default_program"

    steps_list = []
    imagenes = conexion.obtener_image(serial_padre)

    steps_list.append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}_Machine_ID",
        "component_id": machine_id
    })

    steps_list.append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}_Program name + version",
        "component_id": program_version   
    })

    for image in imagenes:
        steps_list.append({
            "name":"RecordMedia","media_identifier":image[2]
        })
    payload = {
        "serial": serial_padre,
        "product": parte[2],
        "station": machine_id,
        "operator": operator_id,
        "password": "",#password,
        "start_time": fecha_formateada,
        "end_time": now_utc,
        "type":tipo,
        "process_name": process_name,
        "commnet": comentario,
        "status": resultado,
        "error_code":error_code,
        "measkey":0,
        "fixture":{
            "tooling_id":"NA",
            "revision":"NA"
        },
        "commands": steps_list
    }

    return payload


# if __name__ == "__main__":
#     resultado_json = traceability_container(
#         serial_padre = "P1472635-61-G:SE4A22172000000",
#         resultado = "PASS",
#         tipo="PRODUCTION",
#         error_code="59dd",
#         comentario="test"
#     )
    
#     if isinstance(resultado_json, dict):
#         print(json.dumps(resultado_json, indent=4))
#     else:
#         print(f"\nError:\n{resultado_json}")