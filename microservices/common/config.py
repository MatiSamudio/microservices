# common/config.py

# Tokens para llamadas internas entre servicios
INTERNAL_PRODUCTS_TOKEN = "SECRET_PRODUCTS_TOKEN"
INTERNAL_ORDERS_TOKEN = "SECRET_ORDERS_TOKEN"
INTERNAL_PAYMENTS_TOKEN = "SECRET_PAYMENTS_TOKEN"

# URLs internas (asumiendo que corrés cada servicio en un puerto distinto)
PRODUCTS_BASE_URL = "http://localhost:5001"
ORDERS_BASE_URL = "http://localhost:5002"
PAYMENTS_BASE_URL = "http://localhost:5003"
