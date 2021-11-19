from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Callable


class MySQLAlchemy(SQLAlchemy):
    Column: Callable  # Use the typing to tell the IDE what the type is
    String: Callable
    Integer: Callable
    Text: Callable
    DateTime: Callable


rental_cars = Flask(__name__)
rental_cars.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_cars.db'
rental_cars.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = MySQLAlchemy(rental_cars)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Order %r>' % self.id


@rental_cars.route('/')
def index():
    return render_template("index.html")


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
