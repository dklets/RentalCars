import sqlite3
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
URL = '/clients-list'


def to_dict(id, passport_number, first_name, last_name, registration_date):
    return {
        "id": id,
        "passport_number": passport_number,
        "first_name": first_name,
        "last_name": last_name,
        "registration_date": registration_date,
    }


@app.before_request
def init_db():
    g.db = sqlite3.connect('/home/dklets/Projects/RentalCars/rental_cars.db')


@app.teardown_request
def close_db(exc):
    g.db.close()


@app.route(URL, methods=["GET"])
def display_clients():
    cursor = g.db.cursor()
    cursor.execute("select id, passport_number, first_name, last_name, registration_date from clients")
    clients = cursor.fetchall()
    cursor.close()
    return jsonify([to_dict(*client) for client in clients])
    # curl http://127.0.0.1:5000/clients-list -v


@app.route(URL, methods=["POST"])
def add_client():
    passport_number = request.json.get('passport_number', '')
    first_name = request.json.get('first_name', '')
    last_name = request.json.get('last_name', '')
    registration_date = request.json.get('registration_date', '')
    if not passport_number or not first_name or not last_name or not registration_date:
        return jsonify({"error": "Incorrect request"}), 400

    cursor = g.db.cursor()
    cursor.execute("Insert into clients \
                   (passport_number,first_name,last_name,registration_date) \
                   values (?,?,?,?)", (passport_number, first_name, last_name, registration_date))
    id = cursor.lastrowid
    cursor.close()
    g.db.commit()
    return jsonify(to_dict(id, passport_number, first_name, last_name, registration_date)), 201
    # curl -X POST http://127.0.0.1:5000/clients-list -H "Content-Type: application/json" -d '{"passport_number": "AX3434XA", "first_name": "Oleksii", "last_name": "Latchenko", "registration_date": "2021-12-28"}' -v


@app.route(f"{URL}/<id>", methods=["PUT"])
def edit_client(id):
    cursor = g.db.cursor()
    cursor.execute("select passport_number, first_name, last_name, registration_date from clients where id=?", (id,))
    client_db = cursor.fetchone()
    cursor.close()
    if client_db is None:
        return jsonify({"error": "Client not found"}), 404

    passport_number, first_name, last_name, registration_date = client_db
    passport_number = request.json.get('passport_number', passport_number)
    first_name = request.json.get('first_name', first_name)
    last_name = request.json.get('last_name', last_name)
    registration_date = request.json.get('registration_date', registration_date)
    cursor = g.db.cursor()

    cursor.execute("update clients set \
                    passport_number=?, first_name=?, last_name=?, registration_date=? \
                    where id=?", (passport_number, first_name, last_name, registration_date, id))
    cursor.close()
    g.db.commit()
    g.db.close()
    return jsonify(to_dict(id, passport_number, first_name, last_name, registration_date))
    # curl -X PUT http://127.0.0.1:5000/clients-list/9 -H "Content-Type: application/json" -d '{"passport_number": "AX3434XA", "first_name": "Oleksii", "last_name": "Latchenko", "registration_date": "2021-12-28"}' -v


@app.route(f"{URL}/<id>", methods=["DELETE"])
def remove_client(id):
    cursor = g.db.cursor()
    cursor.execute("delete from clients where id=?", (id,))
    is_deleted = cursor.rowcount
    cursor.close()
    g.db.commit()
    g.db.close()
    if not is_deleted:
        return jsonify({"error": "Client not found"}), 404
    return "", 204
    # curl -X DELETE http://127.0.0.1:5000/clients-list/13 -v


if __name__ == '__main__':
    app.run(debug=True)
