from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class RestaurantClass(Resource):
    def get(self):
        restaurant_list = [
            restaurant.to_dict(rules=("-restaurant_pizzas",))
            for restaurant in Restaurant.query.all()
        ]
        return make_response(restaurant_list, 200)


api.add_resource(RestaurantClass, "/restaurants")


class RestaurantById(Resource):
    def get(self, id):
        res = Restaurant.query.filter_by(id=id).one_or_none()

        if res is not None:
            return make_response(res.to_dict(), 200)
        else:
            return make_response({"error": "Restaurant not found"}, 404)

    def delete(self, id):
        res = Restaurant.query.filter_by(id=id).one_or_none()

        if res is None:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(res)
        db.session.commit()
        return make_response({}, 204)


api.add_resource(RestaurantById, "/restaurants/<int:id>")


class PizzaClass(Resource):
    def get(self):
        all_pizzas = [
            pizza.to_dict(only=("id", "ingredients", "name"))
            for pizza in Pizza.query.all()
        ]
        return make_response(all_pizzas, 200)


api.add_resource(PizzaClass, "/pizzas")


class RestaurantPizzasClass(Resource):
    def post(self):
        try:
            new_res_pizza = RestaurantPizza(
                price=request.get_json()["price"],
                pizza_id=request.get_json()["pizza_id"],
                restaurant_id=request.get_json()["restaurant_id"],
            )
            db.session.add(new_res_pizza)
            db.session.commit()

            return make_response(new_res_pizza.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(RestaurantPizzasClass, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)