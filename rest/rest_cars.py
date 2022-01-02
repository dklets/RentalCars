import sqlite3
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
URL = '/cars-list'


def to_dict(id, number, description, rental_cost):
    return {
        "id": id,
        "number": number,
        "description": description,
        "rental_cost": rental_cost,
    }


@app.before_request
def init_db():
    g.db = sqlite3.connect('/home/dklets/Projects/RentalCars/rental_cars.db')


@app.teardown_request
def close_db(exc):
    g.db.close()


@app.route(URL, methods=["GET"])
def display_cars():
    cursor = g.db.cursor()
    cursor.execute("select id, number, description, rental_cost from cars")
    cars = cursor.fetchall()
    cursor.close()
    return jsonify([to_dict(*car) for car in cars])
    # curl http://127.0.0.1:5000/cars-list -v


@app.route(URL, methods=["POST"])
def add_car():
    number = request.json.get('number', '')
    description = request.json.get('description', '')
    rental_cost = request.json.get('rental_cost', '')
    if not number or not description or not rental_cost:
        return jsonify({"error": "Incorrect request"}), 400

    cursor = g.db.cursor()
    cursor.execute("Insert into cars (number,description,rental_cost) values (?,?,?)", (number, description, rental_cost))
    id = cursor.lastrowid
    cursor.close()
    g.db.commit()
    return jsonify(to_dict(id, number, description, rental_cost)), 201
    # curl -X POST http://127.0.0.1:5000/cars-list -H "Content-Type: application/json" -d '{"number": "AX9756XA", "description": "Boulevar", "rental_cost": "80"}' -v


@app.route(f"{URL}/<id>", methods=["PUT"])
def edit_car(id):
    cursor = g.db.cursor()
    cursor.execute("select number,description,rental_cost from cars where id=?", (id,))
    car_db = cursor.fetchone()
    cursor.close()
    if car_db is None:
        return jsonify({"error": "Car not found"}), 404

    number, description, rental_cost = car_db
    number = request.json.get("number", number)
    description = request.json.get("description", description)
    rental_cost = request.json.get("rental_cost", rental_cost)
    cursor = g.db.cursor()
    cursor.execute("update cars set number=?, description=?, rental_cost=? where id=?", (number, description, rental_cost, id))
    cursor.close()
    g.db.commit()
    g.db.close()
    return jsonify(to_dict(id, number, description, rental_cost))
    # curl -X PUT http://127.0.0.1:5000/cars-list/11 -H "Content-Type: application/json" -d '{"number": "AX71623", "description": "109EvilG", "rental_cost": "11"}' -v


@app.route(f"{URL}/<id>", methods=["DELETE"])
def remove_car(id):
    cursor = g.db.cursor()
    cursor.execute("delete from cars where id=?", (id,))
    is_deleted = cursor.rowcount
    cursor.close()
    g.db.commit()
    g.db.close()
    if not is_deleted:
        return jsonify({"error": "Car not found"}), 404
    return "", 204
    # curl -X DELETE http://127.0.0.1:5000/cars-list/11 -v


if __name__ == '__main__':
    app.run(debug=True)
