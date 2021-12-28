import sqlite3

from flask import Flask, render_template, url_for, request, redirect, g
from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
from typing import Callable


class MySQLAlchemy(SQLAlchemy):
    Column: Callable  # Use the typing to tell the IDE what the type is
    String: Callable
    Integer: Callable
    Float: Callable
    DateTime: Callable
    ForeignKey: Callable


rental_cars = Flask(__name__)
rental_cars.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_cars.db'
rental_cars.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = MySQLAlchemy(rental_cars)


class Cars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(90), nullable=False)
    rental_cost = db.Column(db.Float(), nullable=False)

    def __repr__(self):
        return f'<cars {self.id}>'


class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passport_number = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    registration_date = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return f'<clients {self.id}>'


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    add_date = db.Column(db.String(45), nullable=False)  # db.Column(db.DateTime, default=datetime.utcnow)
    rental_time = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.String(30), db.ForeignKey('clients.id'))
    car_id = db.Column(db.String(30), db.ForeignKey('cars.id'))

    def __repr__(self):
        return f'<orders {self.id}>'


@rental_cars.route('/')
def index():
    return render_template("index.html")


@rental_cars.route('/add-client', methods=['POST', 'GET'])
def add_client():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        passport_number = request.form['passport_number']
        registration_date = request.form['registration_date']
        client = Clients(first_name=first_name, last_name=last_name, passport_number=passport_number, registration_date=registration_date)
        try:
            db.session.add(client)
            db.session.commit()
            return redirect('/clients-list')
        except:
            return "Error: add client"
    else:
        return render_template("add-client.html")


@rental_cars.route('/add-car', methods=['POST', 'GET'])
def add_car():
    if request.method == 'POST':
        description = request.form['description']
        number = request.form['number']
        rental_cost = request.form['rental_cost']
        car = Cars(description=description, number=number, rental_cost=rental_cost)
        try:
            db.session.add(car)
            db.session.commit()
            return redirect('/cars-list')
        except:
            return "Error: add car"
    else:
        return render_template("add-car.html")


@rental_cars.route('/add-order', methods=['POST', 'GET'])
def add_order():
    clients_list = Clients.query.all()  # get data from sqlite base
    cars_list = Cars.query.all()

    if request.method == 'POST':
        client_id = int(''.join(i for i in request.form['client_id'] if i.isdigit()))
        car_id = int(''.join(i for i in request.form['car_id'] if i.isdigit()))
        rental_time = request.form['rental_time']
        add_date = request.form['add_date']
        order = Orders(client_id=client_id, car_id=car_id, rental_time=rental_time, add_date=add_date)
        try:
            db.session.add(order)
            db.session.commit()
            return redirect('/orders-list')
        except:
            return "Error: add order"
    else:
        return render_template("add-order.html", clients_list=clients_list, cars_list=cars_list)


@rental_cars.route('/orders-list', methods=['POST', 'GET'])
def orders_list():

    orders_req = "SELECT id, number, passport_number, add_date, rental_time, rental_cost, (rental_time * rental_cost) \
                      FROM (SELECT * FROM orders LEFT JOIN clients ON orders.client_id = clients.id \
                      LEFT JOIN cars ON orders.car_id = cars.id)"

    g.db = sqlite3.connect('rental_cars.db')
    cur = g.db.execute(orders_req)
    linked_orders = cur.fetchall()
    g.db.close()

    if request.method == 'POST':  # Take dates from html input "from" and "by" to filter table by date
        date_from = request.form['date_from']
        date_by = request.form['date_by']

        g.db = sqlite3.connect('rental_cars.db')
        cur = g.db.execute(f"SELECT * FROM ({orders_req}) WHERE add_date > '{date_from}' AND add_date < '{date_by}';")
        linked_orders = cur.fetchall()
        g.db.close()

    return render_template('orders-list.html', linked_orders=linked_orders)


@rental_cars.route('/orders-list/<int:id>/update-order', methods=['POST', 'GET'])
def update_order(id):
    clients_list = Clients.query.all()  # get data from sqlite base
    cars_list = Cars.query.all()
    order = Orders.query.get(id)

    if request.method == 'POST':
        order.client_id = int(''.join(i for i in request.form['client_id'] if i.isdigit()))
        order.car_id = int(''.join(i for i in request.form['car_id'] if i.isdigit()))
        order.rental_time = request.form['rental_time']
        order.add_date = request.form['add_date']
        try:
            db.session.commit()
            return redirect('/orders-list')
        except:
            return "Error: edit order"
    else:
        return render_template("update-order.html", order=order, clients_list=clients_list, cars_list=cars_list)


@rental_cars.route('/orders-list/<int:id>/delete-order')
def order_delete(id):
    order = Orders.query.get_or_404(id)

    try:
        db.session.delete(order)
        db.session.commit()
        return redirect('/orders-list')
    except:
        return "Error: delete order"


@rental_cars.route('/clients-list', methods=['POST', 'GET'])
def clients_list():

    clients_req = "SELECT id, first_name, last_name, registration_date, COUNT(client_id) FROM \
                      (SELECT clients.*, orders.client_id FROM clients \
                      LEFT JOIN orders ON clients.id = orders.client_id) GROUP BY id"

    g.db = sqlite3.connect('rental_cars.db')
    cur = g.db.execute(clients_req)
    linked_clients = cur.fetchall()
    g.db.close()

    if request.method == 'POST':  # Take dates from html input "from" and "by" to filter table by date
        date_from = request.form['date_from']
        date_by = request.form['date_by']

        g.db = sqlite3.connect('rental_cars.db')
        cur = g.db.execute(f"SELECT * FROM ({clients_req}) WHERE registration_date > '{date_from}' AND registration_date < '{date_by}';")
        linked_clients = cur.fetchall()
        g.db.close()

    return render_template('clients-list.html', linked_clients=linked_clients)


@rental_cars.route('/clients-list/<int:id>/update-client', methods=['POST', 'GET'])
def update_client(id):
    client = Clients.query.get(id)
    if request.method == 'POST':
        client.first_name = request.form['first_name']
        client.last_name = request.form['last_name']
        client.passport_number = request.form['passport_number']
        client.registration_date = request.form['registration_date']
        try:
            db.session.commit()
            return redirect('/clients-list')
        except:
            return "Error: edit client"
    else:
        return render_template("update-client.html", client=client)


@rental_cars.route('/clients-list/<int:id>/delete-client')
def client_delete(id):
    client = Clients.query.get_or_404(id)

    try:
        db.session.delete(client)
        db.session.commit()
        return redirect('/clients-list')
    except:
        return "Error: delete client"


@rental_cars.route('/cars-list', methods=['POST', 'GET'])
def cars_list():

    cars_req = "SELECT id, description, rental_cost, COUNT(car_id) FROM \
                    (SELECT cars.*, orders.car_id FROM cars \
                    LEFT JOIN orders ON cars.id = orders.car_id) GROUP BY id"

    g.db = sqlite3.connect('rental_cars.db')
    cur = g.db.execute(cars_req)
    linked_cars = cur.fetchall()
    g.db.close()

    if request.method == 'POST':  # Take costs from html input "from" and "by" to filter table by date
        cost_from = request.form['cost_from']
        cost_by = request.form['cost_by']

        g.db = sqlite3.connect('rental_cars.db')
        cur = g.db.execute(f"SELECT * FROM ({cars_req}) WHERE rental_cost > '{cost_from}' AND rental_cost < '{cost_by}';")
        linked_cars = cur.fetchall()
        g.db.close()

    return render_template('cars-list.html', linked_cars=linked_cars)


@rental_cars.route('/cars-list/<int:id>/update-car', methods=['POST', 'GET'])
def update_car(id):
    car = Cars.query.get(id)
    if request.method == 'POST':
        car.description = request.form['description']
        car.number = request.form['number']
        car.rental_cost = request.form['rental_cost']
        try:
            db.session.commit()
            return redirect('/cars-list')
        except:
            return "Error: edit car"
    else:
        return render_template("update-car.html", car=car)


@rental_cars.route('/cars-list/<int:id>/delete-car')
def car_delete(id):
    car = Cars.query.get_or_404(id)

    try:
        db.session.delete(car)
        db.session.commit()
        return redirect('/cars-list')
    except:
        return "Error: delete car"


if __name__ == "__main__":
    rental_cars.run(debug=True)
