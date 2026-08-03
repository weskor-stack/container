import conexion
import requests
import interlocking_json
import json
import container_json
import photo64_v2
import photo_json
import traceability_json

def invoke_api_unit(numero_serie):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api",""
    url_api_unit = url_data[0][0]       # URL Unit API
    url_api_units = url_api_unit.replace("serial_number", numero_serie)
    try:
        response_unit = requests.get(url_api_units, timeout=30)
    except Exception as e:
        return "FAILED",f"Error fetching unit data: {e}",""

    if response_unit.status_code != 200:
        return "FAILED",f"API request failed with status code: {response_unit.status_code}",""

    try:
        json_data_unit = response_unit.json()
    except Exception as e:
        return "FAILED",f"Error parsing JSON: {e}",""

    if not json_data_unit or 'data' not in json_data_unit or not json_data_unit['data']:
        return "FAILED",f"No data found for ISN: {numero_serie}",""

    data_unit = json_data_unit.get('data', {})
    part_number_unit = data_unit.get('part_number', '')

    if not part_number_unit:
        return "FAILED",f"Part number not found for ISN: {numero_serie}",""

    return "PASSED",part_number_unit,json_data_unit

def invoke_api_interlocking(numero_serie, part_number_unit):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api",""
    url_interlocking = url_data[1][0]   # Interlocking API

    interlocking_json_api = interlocking_json.interlocking(
        numero_serie,
        part_number_unit
    )
    
    try:
        response_interlocking = requests.post(
            url_interlocking,
            json=interlocking_json_api,
            timeout=30
        )
    except Exception as e:
        return "FAILED",f"Error invoking interlocking API: {e}",""
                        
    if response_interlocking.status_code != 200:
        return "FAILED",f"Interlocking API request failed with status code: {response_interlocking.status_code}",""

    data_interlocking = response_interlocking.json()

    llamada_interlocking = data_interlocking.get("success", False)

    if llamada_interlocking == "false":
        error_msg = data_interlocking.get("message", "Unknown error")
        return "FAILED",f"Interlocking denied: {error_msg}\n❌ Interlocking API FAILED: {json.dumps(data_interlocking, indent=2)}",""

    if not data_interlocking.get("success", False):
        error_msg = data_interlocking.get("message", "Business rule validation error")
        return "FAILED",f"Interlocking Denied cycle: {error_msg}",""

    return "PASSED",interlocking_json_api,data_interlocking

def invocke_api_conduit_multimedia (serial_number):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api",""

    url_multimedia = url_data[3][0]   # CONDUIT AP

    contenedor_json = container_json.new_container(serial_number)
    # print(json.dumps(contenedor_json, indent=4))
    # print(url_multimedia)

    try:
        response_conduit = requests.post(
            url_multimedia,
            json=contenedor_json,
            timeout=30
        )
    except Exception as e:
        return "FAILED",f"Error invoking interlocking API: {e}","",""

    if response_conduit.status_code != 200:
        return "FAILED",f"Conduit API request failed with status code: {response_conduit.status_code}",f"RESPONSE:\n{json.dumps(response_conduit.json(), indent=4)}",""
    
    data_conduit = response_conduit.json()

    data_unit = data_conduit.get('transaction_responses', {})
    data_command = data_unit[0]
    data_commands = data_command.get('command_responses',{})
    data_commands = data_commands[0]
    data_results = data_commands.get('results',{})
    data_results = data_results[0]
    results = data_results.get('data',{})
    seerial_number = results.get('serial_number','')


    return "PASSED", contenedor_json, data_conduit, seerial_number


def invocke_multimedia_identifier(serial_number):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api",""
                                                    
    url_multimedia = url_data[4][0]   # multimedia API
    # print(url_multimedia)

    foto = photo64_v2.capturar_y_convertir()
    image_json = photo_json.image_json(serial_number,foto)

    try:
        response_multimedia = requests.post(
            url_multimedia,
            json=image_json,
            timeout=30
        )
    except Exception as e:
        return "FAILED",f"Error invoking interlocking API: {e}","",""

    if response_multimedia.status_code != 200:
        return "FAILED",f"Conduit API request failed with status code: {response_multimedia.status_code}",f"RESPONSE:\n{json.dumps(response_multimedia.json(), indent=4)}",""

    data_multimedia = response_multimedia.json()

    llamada_interlocking = data_multimedia.get("success", False)

    if llamada_interlocking == "false":
        error_msg = data_multimedia.get("message", "Unknown error")
        return "FAILED",f"Multimedia API denied: {error_msg}\n❌ Interlocking API FAILED: {json.dumps(data_multimedia, indent=2)}","",""

    if not data_multimedia.get("success", False):
            error_msg = data_multimedia.get("message", "Business rule validation error")
            return "FAILED",f"Multimedia API Denied cycle: {error_msg}","",""

    data_unit = data_multimedia.get('data', {})
    datos = data_unit[0]
    identifier = datos.get('identifier', '')
    
    if not identifier:
        return "FAILED",f"Identifier not found for ISN: {serial_number}","",""
    
    return "PASSED", image_json, data_multimedia, identifier, foto

    # logging.info(f"[MULTIMEDIA JSON]:{image_json}")

def invocke_multimedia(media_identifier):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api","Empty data",""
                                                        
    url_multimedia = url_data[5][0]   # multimedia API
    url_api_multimedia = url_multimedia.replace("media_identifier", media_identifier)
    
    try:
        response_multimedia = requests.get(url_api_multimedia, timeout=30)
    except Exception as e:
        return "FAILED",f"Error fetching unit data: {e}",url_api_multimedia,""
    
    if response_multimedia.status_code != 200:
        return "FAILED",f"API request failed with status code: {response_multimedia.status_code}", url_api_multimedia,""
    
    try:
        json_data_unit = response_multimedia.json()
    except Exception as e:
        return "FAILED",f"Error parsing JSON: {e}",url_api_multimedia,""
    
    if not json_data_unit or 'data' not in json_data_unit or not json_data_unit['data']:
        return "FAILED",f"No data found for identifier: {media_identifier}",url_api_multimedia,""

    return "PASSED",json_data_unit, url_api_multimedia,""

def invocke_traceability(serial_number, resultado, tipo, error_code, comentario):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api","Empty data",""
                                                            
    url_traceability = url_data[2][0]   # Traceability API

    traceability_data = traceability_json.traceability_container(serial_number,resultado, tipo, error_code, comentario)

    try:
        response_traceability = requests.post(
            url_traceability,
            json=traceability_data,
            timeout=30
        )
    except Exception as e:
        return "FAILED",f"Error invoking Traceability API: {e}","",""

    if response_traceability.status_code != 200:
        return "FAILED",f"Conduit API request failed with status code: {response_traceability.status_code}",f"RESPONSE:\n{json.dumps(response_traceability.json(), indent=4)}",""
    
    data_traceability = response_traceability.json()
    
    llamada_traceability = data_traceability.get("success", False)
    
    if llamada_traceability == "false":
        error_msg = data_traceability.get("message", "Unknown error")
        return "FAILED",f"Multimedia API denied: {error_msg}\n❌ Traceability API FAILED: {json.dumps(data_traceability, indent=2)}","",""
    
    if not data_traceability.get("success", False):
        error_msg = data_traceability.get("message", "Business rule validation error")
        return "FAILED",f"Multimedia API Denied cycle: {error_msg}","",""

    return "PASSED",traceability_data, data_traceability,""

def invocke_add_unit_conduit(unidad,pieza):
    url_data = conexion.obtener_url_api()
    if url_data == "FAILED" or not url_data:
        return "FAILED","Database query error in obtener_url_api",""
    
    url_conduit = url_data[3][0]   # CONDUIT AP
    
    unidad_json = container_json.add_component(pieza, unidad)

    try:
        response_conduit = requests.post(
            url_conduit,
            json=unidad_json,
            timeout=30
        )
    except Exception as e:
        return "FAILED",f"Error invoking interlocking API: {e}","",""
    
    if response_conduit.status_code != 200:
        return "FAILED",f"Conduit API request failed with status code: {response_conduit.status_code}",f"RESPONSE:\n{json.dumps(response_conduit.json(), indent=4)}",""
        
    data_conduit = response_conduit.json()

    print(f"RESPONSE CONDUIT:\n{json.dumps(data_conduit, indent=4)}")

    data_unit = data_conduit.get('transaction_responses', {})
    data_command = data_unit[0]
    data_commands = data_command.get('command_responses',{})
    data_commands = data_commands[0]
    data_results = data_commands.get('results',{})
    data_results = data_results[0]
    results = data_results.get('message','')
    
    
    return "PASSED", unidad_json, data_conduit, results

# print(invocke_add_unit_conduit("TEST-12635565465465465","P1472635-61-G:SE4A22172000000"))

# print(invocke_traceability(serial_number = "P1472635-61-G:SE4A22172000000",
#         resultado = "PASS",
#         tipo="PRODUCTION",
#         error_code="59dd",
#         comentario="test"))
# print(invocke_multimedia("54AS33as"))
# print(invoke_api_unit("P1472635-61-G:SE4A22172000000"))
# print(invoke_api_interlocking("P1472635-61-G:SE4A22172000000","LFTM1755080-01-F"))