import enum

class OrderStatus(str, enum.Enum):
    # Основные статусы
    IN_TRANSIT = "in_transit"           # В пути
    ON_ORDER = "on_order"               # Под заказ
    UNPAID = "unpaid"                   # Не оплачен
    PAID_NOT_ISSUED = "paid_not_issued" # Оплачен, не выдан
    PAID_ISSUED = "paid_issued"         # Оплачен и выдан
    PAID_DENIED = "paid_denied"         # Оплачен, но отказано в выдаче
    
    # Статусы доставки
    COURIER_GROZNY = "courier_grozny"   # Курьеру в Грозный
    COURIER_MAK = "courier_mak"         # Курьеру в Махачкалу
    COURIER_KHAS = "courier_khas"       # Курьеру в Хасавюрт
    COURIER_OTHER = "courier_other"     # Курьеру в другой город
    SELF_PICKUP = "self_pickup"         # Ожидает выдачи
    OTHER = "other"                     # Прочие




