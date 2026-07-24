import conexion
import requests
import interlocking_json
import json

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

    

# print(invoke_api_unit("P1472635-61-G:SE4A22172000000"))
# print(invoke_api_interlocking("P1472635-61-G:SE4A22172000000","LFTM1755080-01-F"))