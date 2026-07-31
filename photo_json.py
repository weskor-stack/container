import json
import conexion

def image_json(parent_serial_number,base64):
    
    container = {
        "createdBy":"3131467",
        "storage_level":"site",
        "medias":[
            {
                "tag":" CPI",
                "file_name":f"{parent_serial_number}.png",
                "mime_type":"image/png",
                "data":f"{base64}"
            }
        ]
    }
    # print(json.dumps(container, indent=4))
    return container


# image_json("P1472635-61-G:SE4A22172000000",base64)

