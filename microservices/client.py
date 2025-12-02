import json
import requests

from common.config import (
    PRODUCTS_BASE_URL,
    ORDERS_BASE_URL,
    PAYMENTS_BASE_URL,
    INTERNAL_PRODUCTS_TOKEN,
    INTERNAL_ORDERS_TOKEN,
    INTERNAL_PAYMENTS_TOKEN,
)


# Helpers generales 

def make_headers(token):
    """
    Construye los headers para las requests:
    - Authorization: Bearer <token>
    - Content-Type: application/json
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def send_request(method, url, token, data):
    """
    Helper central para hacer requests a cualquier servicio con:
      - Manejo de errores de conexión.
      - Manejo de timeouts.
      - Impresión estándar de status + body.

    Devuelve:
      - resp (requests.Response) si hubo respuesta del servidor.
      - None si hubo error de red / timeout.
    """
    headers = make_headers(token)

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=3)
        elif method == "POST":
            resp = requests.post(url, headers=headers, data=json.dumps(data or {}), timeout=3)
        elif method == "PUT":
            resp = requests.put(url, headers=headers, data=json.dumps(data or {}), timeout=3)
        else:
            print(f"[CLIENTE] Método HTTP no soportado: {method}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] No se pudo conectar a {url}")
        print("        Verificá que el microservicio correspondiente esté levantado.")
        return None
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Timeout al llamar a {url}")
        print("        El servicio tardó demasiado en responder.")
        return None

    # Si llegamos acá, hubo respuesta HTTP
    print("\n--- Respuesta HTTP ---")
    print("Status:", resp.status_code)
    try:
        print("Body:", resp.json())
    except ValueError:
        print("Body (texto):", resp.text)

    return resp


# Operaciones sobre Productos 

def create_product():
    """
    Pregunta nombre, precio y stock por consola
    Hace POST /products al servicio de Productos
    """
    print("\n=== Crear producto ===")
    name = input("Nombre del producto: ").strip()
    price = float(input("Precio: ").strip())
    stock = int(input("Stock inicial: ").strip())

    url = f"{PRODUCTS_BASE_URL}/products"
    data = {
        "name": name,
        "price": price,
        "stock": stock,
    }

    send_request("POST", url, INTERNAL_PRODUCTS_TOKEN, data)


def list_products():
    """
    Hace GET /products al servicio de Productos
    Imprime el listado
    """
    print("\n=== Listar productos ===")
    url = f"{PRODUCTS_BASE_URL}/products"
    send_request("GET", url, INTERNAL_PRODUCTS_TOKEN)


# Operaciones sobre Pedidos

def create_order():
    """
    Pide product_id y quantity por consola
    Hace POST /orders al servicio de Pedidos
    El microservicio de Pedidos internamente llama a Productos para validar existencia y stock.
    """
    print("\n=== Crear pedido ===")
    product_id = int(input("ID del producto: ").strip())
    quantity = int(input("Cantidad: ").strip())

    url = f"{ORDERS_BASE_URL}/orders"
    data = {
        "product_id": product_id,
        "quantity": quantity,
    }

    send_request("POST", url, INTERNAL_ORDERS_TOKEN, data)


def get_order():
    """
    Pide order_id por consola
    Hace GET /orders/<id> al servicio de Pedidos
    """
    print("\n=== Ver pedido ===")
    order_id = int(input("ID del pedido: ").strip())

    url = f"{ORDERS_BASE_URL}/orders/{order_id}"
    send_request("GET", url, INTERNAL_ORDERS_TOKEN, order_id)


# Operaciones sobre Pagos 

def create_payment():
    """
    Pide order_id, amount y method por consola.
    Hace POST /payments al servicio de Pagos.
    El microservicio de Pagos internamente llama a Orders para validar que el pedido exista.
    """
    print("\n=== Crear pago ===")
    order_id = int(input("ID del pedido: ").strip())
    amount = float(input("Monto a pagar: ").strip())
    method = input("Método de pago (ej: fake-card): ").strip()

    url = f"{PAYMENTS_BASE_URL}/payments"
    data = {
        "order_id": order_id,
        "amount": amount,
        "method": method,
    }

    send_request("POST", url, INTERNAL_PAYMENTS_TOKEN, data)


# Menú principal

def main_menu():
    """
    Menú de texto muy simple.
    Cada opción dispara una función
    """
    while True:
        print("\n=== CLIENTE MICROSERVICIOS ===")
        print("1) Crear producto")
        print("2) Listar productos")
        print("3) Crear pedido")
        print("4) Ver pedido")
        print("5) Crear pago")
        print("0) Salir")

        choice = input("Opción: ").strip()

        if choice == "1":
            create_product()
        elif choice == "2":
            list_products()
        elif choice == "3":
            create_order()
        elif choice == "4":
            get_order()
        elif choice == "5":
            create_payment()
        elif choice == "0":
            print("Saliendo del cliente...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main_menu()
