# orders_service/app.py

from flask import Flask, request, jsonify
from .db import get_connection, init_db
import requests
from common.config import (
    INTERNAL_ORDERS_TOKEN,
    INTERNAL_PRODUCTS_TOKEN,
    PRODUCTS_BASE_URL,
)

app = Flask(__name__)
# Inicializar la DB al arrancar el servicio
init_db()


def check_auth():
    auth_header = request.headers.get("Authorization", "")
    expected = f"Bearer {INTERNAL_ORDERS_TOKEN}"
    return auth_header == expected


def call_products_get(product_id):
    """
    Llama al servicio de productos para obtener un producto.
    """
    url = f"{PRODUCTS_BASE_URL}/products/{product_id}"
    headers = {
        "Authorization": f"Bearer {INTERNAL_PRODUCTS_TOKEN}"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except requests.exceptions.RequestException:
        # Cualquier error de red devolvemos None
        return None

    if resp.status_code == 200: # Si Products responde 200; devuelve el JSON del producto
        return resp.json()
    if resp.status_code == 404: # Si responde 404; no hay producto; None
        return None
    return None


@app.route("/orders", methods=["POST"]) # crea el pedido
def create_order():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if product_id is None or quantity is None:
        return jsonify({"error": "Missing fields"}), 400

    # Verificar producto y stock en el servicio de productos
    product = call_products_get(product_id)
    if product is None:
        return jsonify({"error": "Product not found or unavailable"}), 400

    if product["stock"] < quantity:
        return jsonify({"error": "Not enough stock"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (product_id, quantity, status) VALUES (?, ?, ?)",
        (product_id, quantity, "PENDING")
    )
    conn.commit()
    order_id = cur.lastrowid
    conn.close()

    return jsonify({
        "id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "PENDING"
    }), 201


@app.route("/orders/<int:order_id>", methods=["GET"]) # consultamos pedido por id 
def get_order(order_id):
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, product_id, quantity, status FROM orders WHERE id = ?",
        (order_id,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(dict(row)), 200


if __name__ == "__main__":
    app.run(port=5002, debug=True)
