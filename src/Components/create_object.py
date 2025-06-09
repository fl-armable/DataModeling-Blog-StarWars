# Este script crea un objeto con todos los objetos "result" de Planets.txt y People.txt,
# adaptando las propiedades según tus indicaciones.

import json

# Carga los archivos
with open('/workspaces/DataModeling-Blog-StarWars/src/Components/Planets.txt', 'r') as f:
    planets = json.load(f)

with open('/workspaces/DataModeling-Blog-StarWars/src/Components/People.txt', 'r') as f:
    people = json.load(f)

def adapt_properties(properties, _id):
    # Mantén created, edited, url; el resto los renombra a propertie_1, propertie_2, ...
    result = {
        "propertie_id": _id,
        "created": properties.get("created", ""),
        "edited": properties.get("edited", "")
    }
    # Extrae las claves que no son created, edited, url
    keys = [k for k in properties.keys() if k not in ("created", "edited", "url")]
    # Renombra
    for idx, key in enumerate(keys, 1):
        result[f"propertie_{idx}"] = properties[key]
    # Asegura que haya hasta propertie_9
    for i in range(len(keys)+1, 10):
        result[f"propertie_{i}"] = ""
    result["url"] = properties.get("url", "")
    return result

def adapt_result(obj, type_item):
    result = obj["result"]
    # Cambia _id por prop_id y agrega type_item
    adapted = {
        "prop_id": result["_id"],
        "type_item": type_item,
        "description": result.get("description", ""),
        "uid": result.get("uid", ""),
        "version": result.get("__v", ""),
        "properties": adapt_properties(result["properties"], result["_id"])
    }
    return adapted

# Procesa ambos archivos
all_items = []
for obj in planets:
    all_items.append(adapt_result(obj, "planets"))
for obj in people:
    all_items.append(adapt_result(obj, "people"))

# all_items es la lista de objetos adaptados
# Si quieres verlo como un solo objeto:
result_obj = {"items": all_items}

# Guarda el resultado en items.txt
with open('/workspaces/DataModeling-Blog-StarWars/src/Components/items.txt', 'w') as f:
    f.write(json.dumps(result_obj, indent=4))

# Ejemplo de impresión (opcional)
print("Archivo items.txt creado correctamente.")