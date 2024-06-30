# app.py

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import joinedload  # Import joinedload from sqlalchemy.orm
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

# Custom JSON serialization for SQLAlchemy models
def serialize_model(model, serialized=None):
    if serialized is None:
        serialized = set()

    key = (type(model).__name__, model.id)
    if key in serialized:
        return None  # Prevent recursion

    serialized.add(key)

    result = {}
    for column in model.__table__.columns:
        result[column.name] = getattr(model, column.name)

    for relationship in model.__mapper__.relationships:
        related_obj = getattr(model, relationship.key)
        if related_obj is not None:
            if relationship.uselist:
                result[relationship.key] = [serialize_model(item, serialized) for item in related_obj]
            else:
                result[relationship.key] = serialize_model(related_obj, serialized)

    serialized.remove(key)
    return result if result else None

# Routes
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([serialize_model(restaurant) for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Use db.session.get() instead of Query.get()
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    return jsonify(serialize_model(restaurant))

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Use db.session.get() instead of Query.get()
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([serialize_model(pizza) for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        restaurant_pizza = RestaurantPizza(price=data['price'], pizza_id=data['pizza_id'], restaurant_id=data['restaurant_id'])
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(serialize_model(restaurant_pizza)), 201
    except ValueError as e:
        return jsonify({'errors': [str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
