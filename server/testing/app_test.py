# app_test.py

from sqlalchemy.orm import joinedload  # Import joinedload from sqlalchemy.orm
from models import Restaurant, RestaurantPizza, Pizza
from app import app, db
from faker import Faker

class TestApp:
    '''Flask application in app.py'''

    def test_restaurants_id(self):
        '''retrieves one restaurant using its ID with GET request to /restaurants/<int:id>.'''

        with app.app_context():
            fake = Faker()
            restaurant = Restaurant(name=fake.name(), address=fake.address())
            db.session.add(restaurant)
            db.session.commit()

            # Create a pizza associated with the restaurant
            pizza = Pizza(name=fake.name(), ingredients=fake.sentence())
            db.session.add(pizza)
            db.session.commit()

            # Associate the pizza with the restaurant
            restaurant_pizza = RestaurantPizza(
                restaurant_id=restaurant.id,
                pizza_id=pizza.id,
                price=15  # Example price within valid range
            )
            db.session.add(restaurant_pizza)
            db.session.commit()

            # Fetch the restaurant with its ID and join-load restaurant_pizzas
            restaurant = db.session.get(Restaurant, restaurant.id)

            response = app.test_client().get(f'/restaurants/{restaurant.id}')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            response_json = response.json

            # Assert basic restaurant details
            assert response_json['id'] == restaurant.id
            assert response_json['name'] == restaurant.name
            assert response_json['address'] == restaurant.address

            # Assert 'restaurant_pizzas' is in the response and contains valid data
            assert 'restaurant_pizzas' in response_json
            assert len(response_json['restaurant_pizzas']) == 1  # Assuming only one pizza for simplicity
            assert response_json['restaurant_pizzas'][0]['pizza_id'] == pizza.id
            assert response_json['restaurant_pizzas'][0]['price'] == 15  # Ensure correct price

    # Other test methods remain unchanged
