# payments_service/app.py

from flask import Flask, request, jsonify
from .db import get_connection, init_db
import requests
from common.config import (
    INTERNAL_PAYMENTS_TOKEN,
    INTERNAL_ORDERS_TOKEN,
    ORDERS_BASE_URL,
)

app = Flask(__name__)
# Inicializamos la base de datos al arrancar el servicio
init_db()


def check_auth():
    """
    Verifica que el header Authorization traiga el token de este servicio.
    """
    auth_header = request.headers.get("Authorization", "")
    expected = f"Bearer {INTERNAL_PAYMENTS_TOKEN}"
    return auth_header == expected


def call_orders_get(order_id):
    """
    Llama al servicio de Orders para verificar que el pedido existe
    """
    url = f"{ORDERS_BASE_URL}/orders/{order_id}"
    headers = {
        "Authorization": f"Bearer {INTERNAL_ORDERS_TOKEN}"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=3)
    except requests.exceptions.RequestException:
        # Cualquier error de red o timeout
        return None

    if resp.status_code == 200:
        return resp.json()
    if resp.status_code == 404:
        return None

    # Otros códigos (500, 502, etc.) tambien como fallo
    return None


@app.route("/payments", methods=["POST"]) # crea el pago 
def create_payment():
    """
    Crea un pago para un pedido existente.
    """
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    order_id = data.get("order_id")
    amount = data.get("amount")
    method = data.get("method")

    if order_id is None or amount is None or not method:
        return jsonify({"error": "Missing fields"}), 400

    # Validar que el pedido exista en el servicio Orders
    order = call_orders_get(order_id)
    if order is None:
        # En cualquier caso NO registramos el pago.
        return jsonify({"error": "Order not found or unavailable"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO payments (order_id, amount, method, status) VALUES (?, ?, ?, ?)",
        (order_id, amount, method, "SUCCESS")
    )
    conn.commit()
    payment_id = cur.lastrowid
    conn.close()

    return jsonify({
        "id": payment_id,
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "status": "SUCCESS"
    }), 201


if __name__ == "__main__":
    app.run(port=5003, debug=True)
