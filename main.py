from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Callable
from sqlalchemy.orm import relationship


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
    number = db.Column(db.String(30), primary_key=True)
    description = db.Column(db.String(90), nullable=False)
    rental_cost = db.Column(db.Float(), nullable=False)
    children = relationship("Child")

    def __repr__(self):
        return '<Car %r>' % self.number


class Clients(db.Model):
    passport_number = db.Column(db.String(30), primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    children = relationship("Child")

    def __repr__(self):
        return '<Client %r>' % self.passport_number


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    add_date = db.Column(db.DateTime, default=datetime.utcnow)
    rental_time = db.Column(db.Integer, nullable=False)
    client_passport_number = db.Column(db.String(30), db.ForeignKey('clients.passport_number'))
    car_number = db.Column(db.String(30), db.ForeignKey('cars.number'))

    def __repr__(self):
        return '<Order rental time %r>' % self.id


@rental_cars.route('/')
def index():
    return render_template("index.html")


"""
@rental_cars.route('/create-order', methods=['POST', 'GET'])
def create_order():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        order = Orders(title=title, intro=intro, text=text)

        try:
            db.session.add(order)
            db.session.commit()
            return redirect('/')
        except:
            return "При добавлении заказа произошла ошибка"
    else:
        return render_template("create-order.html")
"""


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
