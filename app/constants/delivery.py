"""
Константы для системы доставки
Определяет типы доставки и их параметры
"""

from enum import Enum

class DeliveryOption(str, Enum):
    """Варианты доставки"""
    SELF_PICKUP_GROZNY = "SELF_PICKUP_GROZNY"      # Самовывоз (Склад, Грозный)
    COURIER_GROZNY = "COURIER_GROZNY"               # Доставка по Грозному
    COURIER_MAK = "COURIER_MAK"                     # Доставка в Махачкалу
    COURIER_KHAS = "COURIER_KHAS"                   # Доставка в Хасавюрт
    COURIER_OTHER = "COURIER_OTHER"                  # Другая (по согласованию)

# Стоимость доставки за единицу товара (в рублях)
DELIVERY_UNIT_PRICE_RUB = 300

# Описания вариантов доставки для пользователя
DELIVERY_OPTIONS_DISPLAY = {
    DeliveryOption.SELF_PICKUP_GROZNY: "Самовывоз (Склад, Грозный)",
    DeliveryOption.COURIER_GROZNY: "Доставка по Грозному",
    DeliveryOption.COURIER_MAK: "Доставка в Махачкалу", 
    DeliveryOption.COURIER_KHAS: "Доставка в Хасавюрт",
    DeliveryOption.COURIER_OTHER: "Другая (по согласованию)"
}

# Варианты доставки, которые требуют ввода города
DELIVERY_OPTIONS_REQUIRE_CITY = {
    DeliveryOption.COURIER_OTHER
}

# Варианты доставки с нулевой стоимостью
DELIVERY_OPTIONS_FREE = {
    DeliveryOption.SELF_PICKUP_GROZNY
}

def calculate_delivery_cost(delivery_option: DeliveryOption, quantity: int) -> int:
    """
    Рассчитывает стоимость доставки
    
    Args:
        delivery_option: Выбранный вариант доставки
        quantity: Количество единиц товара
    
    Returns:
        Стоимость доставки в рублях
    """
    if delivery_option in DELIVERY_OPTIONS_FREE:
        return 0
    
    return DELIVERY_UNIT_PRICE_RUB * quantity

def requires_city_input(delivery_option: DeliveryOption) -> bool:
    """
    Проверяет, требует ли вариант доставки ввода города
    
    Args:
        delivery_option: Выбранный вариант доставки
    
    Returns:
        True если требуется ввод города
    """
    return delivery_option in DELIVERY_OPTIONS_REQUIRE_CITY

def get_delivery_display_name(delivery_option: DeliveryOption) -> str:
    """
    Получает отображаемое название варианта доставки
    
    Args:
        delivery_option: Вариант доставки
    
    Returns:
        Отображаемое название
    """
    return DELIVERY_OPTIONS_DISPLAY.get(delivery_option, str(delivery_option))
