import sqlite3
from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from typing import Callable


class MySQLAlchemy(SQLAlchemy):
    Column: Callable  # Use the typing to tell the IDE what the type is
    String: Callable
    Integer: Callable
    Float: Callable
    DateTime: Callable
    ForeignKey: Callable


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental_cars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = MySQLAlchemy(app)


# app = Flask(__name__)
# db = sqlite3.connect("db.sqlite3")
# cursor = db.cursor()
# cursor.execute("""
#     create table if not exists posts (
#         id integer primary key,
#         name varchar(30),
#         post varchar(140)
#     )
# """)
# cursor.close()
# db.close()


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
    g.db = sqlite3.connect('app.db')


@app.teardown_request
def close_db(exc):
    g.db.close()


@app.route(URL, methods=["POST"])
def create():
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


@app.route(URL, methods=["GET"])
def read_all():
    cursor = g.db.cursor()
    cursor.execute("select id, number, description, rental_cost from cars")
    cars = cursor.fetchall()
    cursor.close()
    return jsonify([to_dict(*cars) for car in cars])


# @app.route(f"{URL}/<id_>", methods=["GET"])
# def read(id_):
#     cursor = g.db.cursor()
#     cursor.execute("select id, name, post from posts where id=?", (id_,))
#     post = cursor.fetchone()
#     cursor.close()
#     if post is None:
#         return jsonify({"error": "Post not found"}), 404
#     return jsonify(to_dict(*post))


# @app.route(f"{URL}/<id_>", methods=["PUT"])
# def update(id_):
#     cursor = g.db.cursor()
#     cursor.execute("select name, post from posts where id=?", (id_,))
#     post_db = cursor.fetchone()
#     cursor.close()
#     if post_db is None:
#         return jsonify({"error": "Post not found"}), 404
#     name, post = post_db
#     name = request.json.get("name", name)
#     post = request.json.get("post", post)
#     cursor = g.db.cursor()
#     cursor.execute("update posts set name=?, post=? where id=?", (name, post, id_))
#     cursor.close()
#     g.db.commit()
#     g.db.close()
#     return jsonify(to_dict(id_, name, post))


# @app.route(f"{URL}/<id_>", methods=["DELETE"])
# def delete(id_):
#     cursor = g.db.cursor()
#     cursor.execute("delete from posts where id=?", (id_,))
#     is_deleted = cursor.rowcount
#     cursor.close()
#     g.db.commit()
#     g.db.close()
#     if not is_deleted:
#         return jsonify({"error": "Post not found"}), 404
#     return "", 204


if __name__ == '__main__':
    app.run(debug=True)
