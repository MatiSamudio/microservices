# Microservices – Minimal Store

Example project to practice **microservices architecture** using Python + Flask + SQLite.

The system simulates an extremely simple store divided into **3 microservices**:

- `products_service`: product management  
- `orders_service`: order management  
- `payments_service`: payment registration  

Each service:

- Has its own REST API  
- Has its own independent database  
- Communicates with other services only through HTTP  
- Is protected by its own `Bearer` token  

---

## 1. General Architecture

Components:

- **Client** (`client.py`):  
  Console script that consumes the APIs of the 3 microservices.

- **Products Service** (`products_service`):  
  Exposes basic CRUD operations for products.  
  Database: `products.db`.

- **Orders Service** (`orders_service`):  
  Creates and retrieves orders.  
  Validates products and stock by calling `products_service` via HTTP.  
  Database: `orders.db`.

- **Payments Service** (`payments_service`):  
  Registers payments associated with orders.  
  Validates order existence by calling `orders_service` via HTTP.  
  Database: `payments.db`.

Each service runs as an independent Flask process on a different port.

---

## 2. Technologies

- **Language:** Python 3  
- **HTTP Framework:** Flask  
- **HTTP Client:** requests  
- **Database:** SQLite (one per microservice)  
- **API Style:** REST (JSON + HTTP status codes)  
- **Authentication between client/services and between services:**  
  Static tokens via header:



---

## 3. Services and APIs

---

### 3.1. Products Service (`products_service`)

- **Port:** `5001`  
- **Base URL:** `http://localhost:5001`  
- **Required token:**



#### Endpoints

1. **GET `/products`**  
 - Returns all products.  
 - 200: list of products.

2. **GET `/products/<id>`**  
 - Returns a product by ID.  
 - 200: product  
 - 404: `{"error": "Product not found"}`

3. **POST `/products`**  
 - Creates a new product.  
 - Body JSON:
   ```json
   {
     "name": "Computer",
     "price": 200,
     "stock": 20
   }
   ```
 - 201: product created

4. **PUT `/products/<id>`**  
 - Fully updates an existing product.  
 - 200: updated product  
 - 404: product not found

---

### 3.2. Orders Service (`orders_service`)

- **Port:** `5002`  
- **Base URL:** `http://localhost:5002`  
- **Required token:**



#### Endpoints

1. **POST `/orders`**  
 - Creates a new order.  
 - Body JSON:
   ```json
   {
     "product_id": 1,
     "quantity": 3
   }
   ```
 - Logic:
   - Calls `GET /products/<product_id>` from the Products service (internal token).  
   - If product does not exist or stock is insufficient → 400  
   - If valid → creates order with status `"PENDING"`  
 - 201: order created  
 - Errors:
   - `"Missing fields"`  
   - `"Product not found or unavailable"`  
   - `"Not enough stock"`

2. **GET `/orders/<id>`**  
 - Retrieves an order by ID.  
 - 200: order (`id`, `product_id`, `quantity`, `status`)  
 - 404: `{"error": "Order not found"}`

---

### 3.3. Payments Service (`payments_service`)

- **Port:** `5003`  
- **Base URL:** `http://localhost:5003`  
- **Required token:**



#### Endpoints

1. **POST `/payments`**  
 - Registers a payment for an order.  
 - Body JSON:
   ```json
   {
     "order_id": 1,
     "amount": 200,
     "method": "fake-card"
   }
   ```
 - Logic:
   - Calls `GET /orders/<order_id>` from the Orders service (internal token).  
   - If the order does not exist or Orders is unavailable → 400 `"Order not found or unavailable"`  
   - If valid → stores payment with status `"SUCCESS"`  
 - 201: payment created  
 - Errors:
   - `"Missing fields"`  
   - `"Order not found or unavailable"`

---

## 4. Project Structure

```text
microservices/

common/
  config.py          # tokens and internal URLs

products_service/
  app.py             # Products HTTP API (Flask)
  db.py              # initialization and access to products.db

orders_service/
  app.py             # Orders HTTP API (Flask)
  db.py              # initialization and access to orders.db

payments_service/
  app.py             # Payments HTTP API (Flask)
  db.py              # initialization and access to payments.db

client.py            # console client to test the 3 services
```

# microservices# Microservicios – Tienda Minimal

Proyecto de ejemplo para practicar arquitectura de **microservicios** usando Python + Flask + SQLite.

El sistema simula una tienda extremadamente simple dividida en 3 microservicios:

- `products_service`: gestión de productos.
- `orders_service`: gestión de pedidos.
- `payments_service`: registro de pagos.

Cada servicio:

- Tiene su propia API REST.
- Tiene su propia base de datos independiente.
- Se comunica con otros servicios solo vía HTTP.
- Está protegido por un token `Bearer` propio.

---

## 1. Arquitectura general

Componentes:

- **Cliente** (`client.py`):
  - Script de consola que consume las APIs de los 3 microservicios.
- **Servicio de Productos** (`products_service`):
  - Expone operaciones CRUD básicas sobre productos.
  - Base de datos: `products.db`.
- **Servicio de Pedidos** (`orders_service`):
  - Crea y consulta pedidos.
  - Valida productos y stock llamando a `products_service` por HTTP.
  - Base de datos: `orders.db`.
- **Servicio de Pagos** (`payments_service`):
  - Registra pagos asociados a pedidos.
  - Valida existencia de pedido llamando a `orders_service` por HTTP.
  - Base de datos: `payments.db`.

Cada servicio es un proceso Flask independiente ejecutándose en un puerto distinto.

---

## 2. Tecnologías

- Lenguaje: **Python 3**
- Framework HTTP: **Flask**
- Cliente HTTP: **requests**
- Base de datos: **SQLite** (una por microservicio)
- Estilo de API: **REST** (JSON + HTTP status codes)
- Autenticación entre cliente/servicios y entre servicios:
  - Tokens estáticos via header:
    - `Authorization: Bearer <TOKEN>`

---

## 3. Servicios y APIs

### 3.1. Servicio de Productos (`products_service`)

- Puerto: `5001`
- Base URL: `http://localhost:5001`
- Token requerido:
  - `Authorization: Bearer SECRET_PRODUCTS_TOKEN`

Endpoints:

1. `GET /products`
   - Lista todos los productos.
   - Respuesta 200: lista de productos.

2. `GET /products/<id>`
   - Obtiene un producto por ID.
   - 200: producto.
   - 404: `{"error": "Product not found"}`.

3. `POST /products`
   - Crea un nuevo producto.
   - Body JSON:
     ```json
     {
       "name": "Computadora",
       "price": 200,
       "stock": 20
     }
     ```
   - 201: producto creado.

4. `PUT /products/<id>`
   - Actualiza por completo un producto existente.
   - 200: producto actualizado.
   - 404: si el producto no existe.

---

### 3.2. Servicio de Pedidos (`orders_service`)

- Puerto: `5002`
- Base URL: `http://localhost:5002`
- Token requerido:
  - `Authorization: Bearer SECRET_ORDERS_TOKEN`

Endpoints:

1. `POST /orders`
   - Crea un nuevo pedido.
   - Body JSON:
     ```json
     {
       "product_id": 1,
       "quantity": 3
     }
     ```
   - Lógica:
     - Llama a `GET /products/<product_id>` del servicio de Productos (con token interno).
     - Si el producto no existe o no hay stock suficiente → 400.
     - Si todo está bien → crea pedido con estado `"PENDING"`.
   - 201: pedido creado.
   - Errores:
     - 400: `"Missing fields"`, `"Product not found or unavailable"`, `"Not enough stock"`.

2. `GET /orders/<id>`
   - Obtiene un pedido por ID.
   - 200: pedido (id, product_id, quantity, status).
   - 404: `{"error": "Order not found"}`.

---

### 3.3. Servicio de Pagos (`payments_service`)

- Puerto: `5003`
- Base URL: `http://localhost:5003`
- Token requerido:
  - `Authorization: Bearer SECRET_PAYMENTS_TOKEN`

Endpoints:

1. `POST /payments`
   - Registra un pago para un pedido.
   - Body JSON:
     ```json
     {
       "order_id": 1,
       "amount": 200,
       "method": "fake-card"
     }
     ```
   - Lógica:
     - Llama a `GET /orders/<order_id>` del servicio de Pedidos (con token interno).
     - Si el pedido no existe o Orders está caído → 400 `"Order not found or unavailable"`.
     - Si el pedido existe → inserta pago con estado `"SUCCESS"`.
   - 201: pago creado.
   - Errores:
     - 400: `"Missing fields"`, `"Order not found or unavailable"`.

---

## 4. Estructura del proyecto

```text
microservices/

  common/
    config.py          # tokens y URLs internas

  products_service/
    app.py             # API HTTP de productos (Flask)
    db.py              # inicialización y acceso a products.db

  orders_service/
    app.py             # API HTTP de pedidos (Flask)
    db.py              # inicialización y acceso a orders.db

  payments_service/
    app.py             # API HTTP de pagos (Flask)
    db.py              # inicialización y acceso a payments.db

  client.py            # cliente de consola para probar los 3 servicios
