# products_service/app.py

from flask import Flask, request, jsonify
from .db import get_connection, init_db
from common.config import INTERNAL_PRODUCTS_TOKEN

app = Flask(__name__)

# Inicializamos la base de datos al arrancar el servicio
init_db()

def check_auth():
    '''autoriza en base al header(el token que lleva debe coincidir con el token de este servicio)'''
    auth_header = request.headers.get("Authorization", "")
    expected = f"Bearer {INTERNAL_PRODUCTS_TOKEN}"
    if auth_header != expected:
        return False
    return True

@app.route("/products", methods=["GET"]) # trae todos los productos
def list_products():
    '''Devuelve una lista con todos los rows de la db'''
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products")
    rows = cur.fetchall()
    conn.close()

    products = [dict(row) for row in rows]
    return jsonify(products), 200

@app.route("/products/<int:product_id>", methods=["GET"]) # trae un producto por id
def get_product(product_id):
    '''Busca producto por id, si no existe devuelve error'''
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(dict(row)), 200

@app.route("/products", methods=["POST"]) # crea un producto nuevo 
def create_product():
    '''Pide todos los campos para insertar en la db'''
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    if not name or price is None or stock is None:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (name, price, stock)
    )
    conn.commit()
    product_id = cur.lastrowid
    conn.close()

    return jsonify({"id": product_id, "name": name, "price": price, "stock": stock}), 201

@app.route("/products/<int:product_id>", methods=["PUT"]) # actualiza un producto. PUT para reemplazar/actualizar el recurso
def update_product(product_id):
    '''Checkea que exista el producto con el id y pide todos los campos para actualizar'''
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    if not name or price is None or stock is None:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    cur.execute(
        "UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?",
        (name, price, stock, product_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"id": product_id, "name": name, "price": price, "stock": stock}), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)
