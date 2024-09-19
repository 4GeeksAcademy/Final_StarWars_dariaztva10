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
from models import db, User, Planet, Character, Favorite
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
# Endpoint para listar o crear usuarios
@app.route('/user', methods=['GET', 'POST'])
def handle_user():
    if request.method == 'GET':
        users = User.query.all()
        users = [user.to_dict() for user in users]
        return jsonify({"data": users}), 200
    elif request.method == 'POST':
        data = request.get_json()
        user = User(name=data["name"], username=data["username"], password=data["password"])
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User created"}), 201

# Endpoint para manejar un usuario específico por id (GET, PUT, DELETE)
@app.route("/user/<int:id>", methods=["GET", "PUT", "DELETE"])
def update_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"msg": f"User with id {id} not found"}), 404
    
    if request.method == 'GET':
        return jsonify(user.to_dict()), 200
    elif request.method == 'PUT':
        data = request.get_json()
        user.name = data["name"]
        user.username = data["username"]
        db.session.commit()
        return jsonify({"msg": "User updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted"}), 202

# Endpoint para manejar personajes (GET, POST)
@app.route('/character', methods=['GET', 'POST'])
def handle_character():
    if request.method == 'GET':
        characters = Character.query.all()
        characters = [character.to_dict() for character in characters]
        return jsonify({"data": characters}), 200
    elif request.method == 'POST':
        data = request.get_json()
        character = Character(name=data["name"])
        db.session.add(character)
        db.session.commit()
        return jsonify({"msg": "Character created"}), 201

# Endpoint para manejar un personaje específico por id (PUT, DELETE)
@app.route("/character/<int:id>", methods=["PUT", "DELETE"])
def update_character(id):
    character = Character.query.get(id)
    if not character:
        return jsonify({"msg": f"Character with id {id} not found"}), 404

    if request.method == 'PUT':
        data = request.get_json()
        character.name = data["name"]
        db.session.commit()
        return jsonify({"msg": "Character updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(character)
        db.session.commit()
        return jsonify({"msg": "Character deleted"}), 202

# Endpoint para manejar planetas (GET, POST)
@app.route('/planet', methods=['GET', 'POST'])
def handle_planet():
    if request.method == 'GET':
        planets = Planet.query.all()
        planets = [planet.to_dict() for planet in planets]
        return jsonify({"data": planets}), 200
    elif request.method == 'POST':
        data = request.get_json()
        planet = Planet(name=data["name"])
        db.session.add(planet)
        db.session.commit()
        return jsonify({"msg": "Planet created"}), 201

# Endpoint para manejar un planeta específico por id (PUT, DELETE)
@app.route("/planet/<int:id>", methods=["PUT", "DELETE", "GET"])
def update_planet(id):
    planet = Planet.query.get(id)
    if not planet:
        return jsonify({"msg": f"Planet with id {id} not found"}), 404
    if request.method == 'GET':
    
       return jsonify({"msg": planet.serialize()}), 200
    if request.method == 'PUT':
        data = request.get_json()
        planet.name = data["name"]
        db.session.commit()
        return jsonify({"msg": "Planet updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg": "Planet deleted"}), 202

# Endpoint para manejar los favoritos de un usuario
@app.route('/user/<int:id>/favorite', methods=['GET'])
def handle_favorite(id):
    favorites = Favorite.query.filter_by(user_id=id).all()
    if not favorites:
        return jsonify({"msg": "No favorites found"}), 404

    favorites = [favorite.to_dict() for favorite in favorites]
    return jsonify({"data": favorites}), 200

# Endpoint para agregar un favorito de personaje
@app.route('/user/<int:id>/favorite/character', methods=['POST'])
def add_favorite_character(id):
    data = request.get_json()
    favorite = Favorite(user_id=id, character_id=data["character_id"])
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite character added"}), 201

# Endpoint para agregar un favorito de planeta
@app.route('/user/<int:id>/favorite/planet', methods=['POST'])
def add_favorite_planet(id):
    data = request.get_json()
    favorite = Favorite(user_id=id, planet_id=data["planet_id"])
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite planet added"}), 201

# Ejecutar la aplicación
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0')

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
