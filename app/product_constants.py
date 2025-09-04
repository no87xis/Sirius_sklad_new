"""
Константы для статусов товаров
"""

# Статусы наличия товаров
class ProductStatus:
    IN_STOCK = "IN_STOCK"      # В наличии
    ON_ORDER = "ON_ORDER"      # Под заказ
    IN_TRANSIT = "IN_TRANSIT"  # В пути
    OUT_OF_STOCK = "OUT_OF_STOCK"  # Нет в наличии

# Список всех возможных статусов
PRODUCT_STATUSES = [
    ProductStatus.IN_STOCK,
    ProductStatus.ON_ORDER,
    ProductStatus.IN_TRANSIT,
    ProductStatus.OUT_OF_STOCK
]

# Статус по умолчанию
DEFAULT_STATUS = ProductStatus.IN_STOCK





