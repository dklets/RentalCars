import sqlite3
from flask import Flask, request, jsonify, g

app = Flask(__name__)
db = sqlite3.connect("db.sqlite3")
cursor = db.cursor()
cursor.execute("""
    create table if not exists posts (
        id integer primary key,
        name varchar(30),
        post varchar(140)
    )
""")
cursor.close()
db.close()

URL = '/posts'


def to_dict(id_, name, post):
    return {
        "id": id_,
        "name": name,
        "post": post,
    }


@app.before_request
def init_db():
    g.db = sqlite3.connect("db.sqlite3")


@app.teardown_request
def close_db(exc):
    g.db.close()


@app.route(URL, methods=["POST"])
def create():
    name = request.json.get('name', '')
    post = request.json.get('post', '')
    if not name or not post:
        return jsonify({"error": "Incorrect request"}), 400

    cursor = g.db.cursor()
    cursor.execute("insert into posts (name, post) values (?, ?)", (name, post))
    id_ = cursor.lastrowid
    cursor.close()
    g.db.commit()
    return jsonify(to_dict(id_, name, post)), 201


@app.route(URL, methods=["GET"])
def read_all():
    cursor = g.db.cursor()
    cursor.execute("select id, name, post from posts")
    posts = cursor.fetchall()
    cursor.close()
    return jsonify([to_dict(*post) for post in posts])


@app.route(f"{URL}/<id_>", methods=["GET"])
def read(id_):
    cursor = g.db.cursor()
    cursor.execute("select id, name, post from posts where id=?", (id_,))
    post = cursor.fetchone()
    cursor.close()
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(to_dict(*post))


@app.route(f"{URL}/<id_>", methods=["PUT"])
def update(id_):
    cursor = g.db.cursor()
    cursor.execute("select name, post from posts where id=?", (id_,))
    post_db = cursor.fetchone()
    cursor.close()
    if post_db is None:
        return jsonify({"error": "Post not found"}), 404
    name, post = post_db
    name = request.json.get("name", name)
    post = request.json.get("post", post)
    cursor = g.db.cursor()
    cursor.execute("update posts set name=?, post=? where id=?", (name, post, id_))
    cursor.close()
    g.db.commit()
    g.db.close()
    return jsonify(to_dict(id_, name, post))


@app.route(f"{URL}/<id_>", methods=["DELETE"])
def delete(id_):
    cursor = g.db.cursor()
    cursor.execute("delete from posts where id=?", (id_,))
    is_deleted = cursor.rowcount
    cursor.close()
    g.db.commit()
    g.db.close()
    if not is_deleted:
        return jsonify({"error": "Post not found"}), 404
    return "", 204


if __name__ == '__main__':
    app.run(debug=True)
