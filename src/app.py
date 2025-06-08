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
from models import db, User, Item, Properties
#from models import Person

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
        ok_item, _ = Item.add_item({
            "type_item": item["type_item"],
            "prop_id": item["prop_id"],
            "description": item.get("description", ""),
            "uid": item.get("uid", ""),
            "version": item.get("version", 1)
        })
        if not ok_item:
            db.session.rollback()
            return jsonify({"done": False, "message": f"Error loading item {item.get('prop_id', '')}"}), 400
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

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
