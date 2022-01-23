import sqlite3
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
URL = '/orders-list'


def to_dict(id, add_date, rental_time, client_id, car_id):
    return {
        "id": id,
        "add_date": add_date,
        "rental_time": rental_time,
        "client_id": client_id,
        "car_id": car_id,
    }


@app.before_request
def init_db():
    g.db = sqlite3.connect('/home/dklets/Projects/RentalCars/rental_cars.db')


@app.teardown_request
def close_db(exc):
    g.db.close()


@app.route(URL, methods=["GET"])
def display_orders():
    cursor = g.db.cursor()
    cursor.execute("select id, add_date, rental_time, client_id, car_id from orders")
    orders = cursor.fetchall()
    cursor.close()
    return jsonify([to_dict(*order) for order in orders])
    # curl http://127.0.0.1:5000/orders-list -v


@app.route(URL, methods=["POST"])
def add_order():
    add_date = request.json.get('add_date', '')
    rental_time = request.json.get('rental_time', '')
    client_id = request.json.get('client_id', '')
    car_id = request.json.get('car_id', '')
    if not add_date or not rental_time or not client_id or not car_id:
        return jsonify({"error": "Incorrect request"}), 400

    cursor = g.db.cursor()
    cursor.execute("Insert into orders \
                   (add_date, rental_time, client_id, car_id) \
                   values (?,?,?,?)", (add_date, rental_time, client_id, car_id))
    id = cursor.lastrowid
    cursor.close()
    g.db.commit()
    return jsonify(to_dict(id, add_date, rental_time, client_id, car_id)), 201
    # curl -X POST http://127.0.0.1:5000/orders-list -H "Content-Type: application/json" -d '{"add_date": "2021-12-28", "rental_time": "3", "client_id": "3", "car_id": "3"}' -v


@app.route(f"{URL}/<id>", methods=["PUT"])
def edit_order(id):
    cursor = g.db.cursor()
    cursor.execute("select add_date, rental_time, client_id, car_id from orders where id=?", (id,))
    order_db = cursor.fetchone()
    cursor.close()
    if order_db is None:
        return jsonify({"error": "Order not found"}), 404

    add_date, rental_time, client_id, car_id = order_db
    add_date = request.json.get('add_date', add_date)
    rental_time = request.json.get('rental_time', rental_time)
    client_id = request.json.get('client_id', client_id)
    car_id = request.json.get('car_id', car_id)
    cursor = g.db.cursor()

    cursor.execute("update orders set \
                    add_date=?, rental_time=?, client_id=?, car_id=? \
                    where id=?", (add_date, rental_time, client_id, car_id, id))
    cursor.close()
    g.db.commit()
    g.db.close()
    return jsonify(to_dict(id, add_date, rental_time, client_id, car_id))
    # curl -X PUT http://127.0.0.1:5000/orders-list/16 -H "Content-Type: application/json" -d '{"add_date": "2021-12-24", "rental_time": "1", "client_id": "1", "car_id": "1"}' -v


@app.route(f"{URL}/<id>", methods=["DELETE"])
def remove_order(id):
    cursor = g.db.cursor()
    cursor.execute("delete from orders where id=?", (id,))
    is_deleted = cursor.rowcount
    cursor.close()
    g.db.commit()
    g.db.close()
    if not is_deleted:
        return jsonify({"error": "Order not found"}), 404
    return "", 204
    # curl -X DELETE http://127.0.0.1:5000/orders-list/16 -v


if __name__ == '__main__':
    app.run(debug=True)
