from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Callable
# from sqlalchemy.orm import relationship


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
    # children = relationship("Child")

    def __repr__(self):
        return f'<cars {self.id}>'


class Clients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passport_number = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    registration_date = db.Column(db.String(45), nullable=False)
    # children = relationship("Child")

    def __repr__(self):
        return f'<clients {self.id}>'


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    add_date = db.Column(db.DateTime, default=datetime.utcnow)
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
            return redirect('/')
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
            return redirect('/')
        except:
            return "Error: add car"
    else:
        return render_template("add-car.html")


@rental_cars.route('/department')
def department():
    return render_template("department.html")


@rental_cars.route('/departments')
def departments():
    return render_template("departments.html")


@rental_cars.route('/employee')
def employee():
    return render_template("employee.html")


@rental_cars.route('/employees')
def employees():
    return render_template("employees.html")


if __name__ == "__main__":
    rental_cars.run(debug=True)
