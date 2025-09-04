from .order_status_enum import OrderStatus

# Отображаемые названия статусов
ORDER_STATUS_DISPLAY = {
    OrderStatus.IN_TRANSIT: "В пути",
    OrderStatus.ON_ORDER: "Под заказ", 
    OrderStatus.UNPAID: "Не оплачен",
    OrderStatus.PAID_NOT_ISSUED: "Оплачен, не выдан",
    OrderStatus.PAID_ISSUED: "Оплачен и выдан",
    OrderStatus.PAID_DENIED: "Оплачен, но отказано в выдаче",
    OrderStatus.COURIER_GROZNY: "Курьеру в Грозный",
    OrderStatus.COURIER_MAK: "Курьеру в Махачкалу",
    OrderStatus.COURIER_KHAS: "Курьеру в Хасавюрт",
    OrderStatus.COURIER_OTHER: "Курьеру в другой город",
    OrderStatus.SELF_PICKUP: "Ожидает выдачи",
    OrderStatus.OTHER: "Прочие"
}

# Цвета для статусов
ORDER_STATUS_COLORS = {
    OrderStatus.IN_TRANSIT: "bg-blue-100 text-blue-800",
    OrderStatus.ON_ORDER: "bg-yellow-100 text-yellow-800",
    OrderStatus.UNPAID: "bg-red-100 text-red-800",
    OrderStatus.PAID_NOT_ISSUED: "bg-orange-100 text-orange-800",
    OrderStatus.PAID_ISSUED: "bg-green-100 text-green-800",
    OrderStatus.PAID_DENIED: "bg-red-100 text-red-800",
    OrderStatus.COURIER_GROZNY: "bg-purple-100 text-purple-800",
    OrderStatus.COURIER_MAK: "bg-indigo-100 text-indigo-800",
    OrderStatus.COURIER_KHAS: "bg-pink-100 text-pink-800",
    OrderStatus.COURIER_OTHER: "bg-gray-100 text-gray-800",
    OrderStatus.SELF_PICKUP: "bg-green-100 text-green-800",
    OrderStatus.OTHER: "bg-gray-100 text-gray-800"
}

# Иконки для статусов
ORDER_STATUS_ICONS = {
    OrderStatus.IN_TRANSIT: "fas fa-truck",
    OrderStatus.ON_ORDER: "fas fa-clock",
    OrderStatus.UNPAID: "fas fa-times-circle",
    OrderStatus.PAID_NOT_ISSUED: "fas fa-check-circle",
    OrderStatus.PAID_ISSUED: "fas fa-check-double",
    OrderStatus.PAID_DENIED: "fas fa-ban",
    OrderStatus.COURIER_GROZNY: "fas fa-motorcycle",
    OrderStatus.COURIER_MAK: "fas fa-motorcycle",
    OrderStatus.COURIER_KHAS: "fas fa-motorcycle",
    OrderStatus.COURIER_OTHER: "fas fa-motorcycle",
    OrderStatus.SELF_PICKUP: "fas fa-store",
    OrderStatus.OTHER: "fas fa-question"
}

def get_status_display(status: OrderStatus) -> str:
    """Получает отображаемое название статуса"""
    return ORDER_STATUS_DISPLAY.get(status, str(status))

def get_status_color(status: OrderStatus) -> str:
    """Получает CSS классы для цвета статуса"""
    return ORDER_STATUS_COLORS.get(status, "bg-gray-100 text-gray-800")

def get_status_icon(status: OrderStatus) -> str:
    """Получает иконку для статуса"""
    return ORDER_STATUS_ICONS.get(status, "fas fa-question")

def get_all_statuses() -> list:
    """Получает список всех статусов для фильтрации"""
    return [
        (OrderStatus.IN_TRANSIT, get_status_display(OrderStatus.IN_TRANSIT)),
        (OrderStatus.ON_ORDER, get_status_display(OrderStatus.ON_ORDER)),
        (OrderStatus.UNPAID, get_status_display(OrderStatus.UNPAID)),
        (OrderStatus.COURIER_GROZNY, get_status_display(OrderStatus.COURIER_GROZNY)),
        (OrderStatus.COURIER_MAK, get_status_display(OrderStatus.COURIER_MAK)),
        (OrderStatus.COURIER_KHAS, get_status_display(OrderStatus.COURIER_KHAS)),
        (OrderStatus.SELF_PICKUP, get_status_display(OrderStatus.SELF_PICKUP)),
        (OrderStatus.OTHER, get_status_display(OrderStatus.OTHER))
    ]

