"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Item, Properties, Favorites
from datetime import datetime, timezone

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/items', methods=['POST'])
def load_data():
    data = request.get_json()
    if not data or "items" not in data:
        return jsonify({"done": False, "message": "Invalid input"}), 400

    for item in data["items"]:
        # Validar si prop_id ya existe en la base de datos
        exists = db.session.query(Item).filter_by(prop_id=item["prop_id"]).first()
        if exists:
            continue
        # Cargar el item
        ok_item, error_item = Item.add_item({
            "type_item": item["type_item"],
            "prop_id": item["prop_id"],
            "description": item.get("description", ""),
            "uid": item.get("uid", ""),
            "version": item.get("version", 1)
        })
        if not ok_item:
            db.session.rollback()
            return jsonify({"done": False, "message": f"Error loading item {item.get('prop_id', '')}", "error": error_item}), 400
        # Cargar las properties asociadas
        prop = item.get("properties", {})
        ok_prop, _ = Properties.add_propertie({
            "propertie_id": prop.get("propertie_id", ""),
            "created": prop.get("created", ""),
            "edited": prop.get("edited", ""),
            "propertie_1": prop.get("propertie_1", ""),
            "propertie_2": prop.get("propertie_2", ""),
            "propertie_3": prop.get("propertie_3", ""),
            "propertie_4": prop.get("propertie_4", ""),
            "propertie_5": prop.get("propertie_5", ""),
            "propertie_6": prop.get("propertie_6", ""),
            "propertie_7": prop.get("propertie_7", ""),
            "propertie_8": prop.get("propertie_8", ""),
            "propertie_9": prop.get("propertie_9", ""),
            "url": prop.get("url", "")
        })
        if not ok_prop:
            db.session.rollback()
            return jsonify({"done": False, "message": f"Error loading properties for {prop.get('propertie_id', '')}"}), 400

    return jsonify({"done": True, "message": "Object was successfully"}), 200

# Mapeos de claves para properties según el tipo de item
PEOPLE_PROPERTIES = [
    ("propertie_1", "name"),
    ("propertie_2", "gender"),
    ("propertie_3", "skin_color"),
    ("propertie_4", "hair_color"),
    ("propertie_5", "height"),
    ("propertie_6", "eye_color"),
    ("propertie_7", "mass"),
    ("propertie_8", "homeworld"),
    ("propertie_9", "birth_year"),
]

PLANETS_PROPERTIES = [
    ("propertie_1", "climate"),
    ("propertie_2", "surface_water"),
    ("propertie_3", "name"),
    ("propertie_4", "diameter"),
    ("propertie_5", "rotation_period"),
    ("propertie_6", "terrain"),
    ("propertie_7", "gravity"),
    ("propertie_8", "orbital_period"),
    ("propertie_9", "population"),
]

@app.route('/items/<type_item>/<uid>', methods=['GET'])
def get_item_by_type_and_uid(type_item, uid):
    ok, item = Item.get_item(type_item, uid)
    if not ok or not item:
        return jsonify({"done": False, "message": "Item not found"}), 404

    # Buscar las properties asociadas
    prop_ok, prop = Properties.get_propertie(item["prop_id"])
    if not prop_ok or not prop:
        return jsonify({"done": False, "message": "Properties not found"}), 404

    # Seleccionar el mapeo de claves según el tipo
    if type_item.lower() == "people":
        prop_map = PEOPLE_PROPERTIES
    elif type_item.lower() == "planets":
        prop_map = PLANETS_PROPERTIES
    else:
        return jsonify({"done": False, "message": "Invalid type_item"}), 400

    # Construir el dict de properties con los nombres correctos
    properties = {
        "created": prop["created"],
        "edited": prop["edited"],
        "url": prop["url"]
    }
    for db_key, api_key in prop_map:
        properties[api_key] = prop[db_key]

    result = {
        "properties": properties,
        "description": item["description"],
        "uid": item["uid"],
        "__v": item["version"]
    }

    response = {
        "result": result
    }
    return jsonify(response), 200

@app.route('/items/<type_item>/<uid>', methods=['DELETE'])
def delete_item(type_item, uid):
    # Buscar el item por tipo y uid
    item = db.session.query(Item).filter_by(type_item=type_item, uid=uid).first()
    if not item:
        return jsonify({"done": False, "message": "Item not found"}), 404

    # Eliminar las properties asociadas
    prop = db.session.query(Properties).filter_by(propertie_id=item.prop_id).first()
    if prop:
        db.session.delete(prop)

    # Eliminar el item
    db.session.delete(item)
    db.session.commit()

    return jsonify({"done": True, "message": "Item deleted successfully"}), 200

@app.route('/items/<type_item>/<uid>', methods=['PUT'])
def update_item(type_item, uid):
    data = request.get_json()
    if not data or "description" not in data or "properties" not in data:
        return jsonify({"done": False, "message": "Invalid input"}), 400

    # Buscar el item por tipo y uid
    item = db.session.query(Item).filter_by(type_item=type_item, uid=uid).first()
    if not item:
        return jsonify({"done": False, "message": "Item not found"}), 404

    # Actualizar el item
    item.description = data["description"]
    item.version += 1
    db.session.commit()
    # Actualizar las properties asociadas
    prop = db.session.query(Properties).filter_by(propertie_id=item.prop_id).first()
    if not prop or "properties" not in data:
        return jsonify({"done": False, "message": "Properties not found"}), 404
    # Validar que las propiedades a cambiar existan en el modelo Properties
    valid_keys = {
        "created", "edited", "url",
        "propertie_1", "propertie_2", "propertie_3", "propertie_4", "propertie_5",
        "propertie_6", "propertie_7", "propertie_8", "propertie_9"
    }
    for key in data["properties"].keys():
        if key not in valid_keys:
            return jsonify({"done": False, "message": f"La propiedad '{key}' no existe en Properties"}), 400
    prop.created = data["properties"].get("created", prop.created)
    prop.edited = data["properties"].get("edited", prop.edited)
    prop.url = data["properties"].get("url", prop.url)
    prop.propertie_1 = data["properties"].get("propertie_1", prop.propertie_1)
    prop.propertie_2 = data["properties"].get("propertie_2", prop.propertie_2)
    prop.propertie_3 = data["properties"].get("propertie_3", prop.propertie_3)
    prop.propertie_4 = data["properties"].get("propertie_4", prop.propertie_4)
    prop.propertie_5 = data["properties"].get("propertie_5", prop.propertie_5)
    prop.propertie_6 = data["properties"].get("propertie_6", prop.propertie_6)
    prop.propertie_7 = data["properties"].get("propertie_7", prop.propertie_7)
    prop.propertie_8 = data["properties"].get("propertie_8", prop.propertie_8)
    prop.propertie_9 = data["properties"].get("propertie_9", prop.propertie_9)
    db.session.commit()
    return jsonify({"done": True, "message": "Item updated successfully"}), 200

@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"done": False, "message": "Faltan campos requeridos"}), 400

    user_data = {
        "email": data["email"],
        "password": data["password"],
        "member_since": datetime.now(timezone.utc)
    }
    ok, result = User.add_user(user_data)
    if ok:
        return jsonify({"done": True, "user": result}), 201
    else:
        return jsonify({"done": False, "message": "No se pudo crear el usuario", "error": result.get("error", "")}), 400

@app.route('/user', methods=['GET'])
def get_users():
    response_body = User.get_users()
    return jsonify(response_body), 200

@app.route('/favorites/<type_item>/<uid>', methods=['POST'])
def add_favorite(type_item, uid):
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id es requerido"}), 400

    # Buscar el item correspondiente
    item = db.session.query(Item).filter_by(type_item=type_item, uid=uid).first()
    if not item:
        return jsonify({"error": "Item no encontrado"}), 404

    # Agregar a favoritos
    success, result = Favorites.add_favorites(user_id=user_id, item_id=item.id)
    if success:
        return jsonify(result), 201
    else:
        return jsonify({"error": "No se pudo agregar a favoritos"}), 400
    
@app.route('/favorites/user/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    favorites = Favorites.get_favorites(user_id)
    return jsonify(favorites), 200

@app.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    success = Favorites.delete_favorites(favorite_id)
    if success:
        return jsonify({"msg": "Favorito eliminado"}), 200
    else:
        return jsonify({"error": "No se pudo eliminar el favorito"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
