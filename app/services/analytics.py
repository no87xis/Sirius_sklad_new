from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import Order, Product, Supply, OrderStatus
import csv
import io

def get_sales_report(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, product_id: Optional[int] = None) -> Dict[str, Any]:
    """Получить отчет по продажам"""
    query = db.query(Order).filter(Order.status == OrderStatus.PAID_ISSUED)
    
    if start_date:
        query = query.filter(Order.issued_at >= start_date)
    if end_date:
        query = query.filter(Order.issued_at <= end_date)
    if product_id:
        query = query.filter(Order.product_id == product_id)
    
    orders = query.all()
    
    # Общая статистика
    total_orders = len(orders)
    total_revenue = sum(order.qty * order.unit_price_rub for order in orders)
    total_quantity = sum(order.qty for order in orders)
    
    # Статистика по товарам
    product_stats = {}
    for order in orders:
        if order.product_id not in product_stats:
            product_stats[order.product_id] = {
                'product_name': order.product_name,
                'quantity': 0,
                'revenue': Decimal('0'),
                'orders_count': 0
            }
        product_stats[order.product_id]['quantity'] += order.qty
        product_stats[order.product_id]['revenue'] += order.qty * order.unit_price_rub
        product_stats[order.product_id]['orders_count'] += 1
    
    # Статистика по дням
    daily_stats = {}
    for order in orders:
        if order.issued_at:
            date_key = order.issued_at.date()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'quantity': 0,
                    'revenue': Decimal('0'),
                    'orders_count': 0
                }
            daily_stats[date_key]['quantity'] += order.qty
            daily_stats[date_key]['revenue'] += order.qty * order.unit_price_rub
            daily_stats[date_key]['orders_count'] += 1
    
    return {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'product_stats': list(product_stats.values()),
        'daily_stats': sorted(daily_stats.values(), key=lambda x: x['date']),
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    }

def get_inventory_report(db: Session) -> Dict[str, Any]:
    """Получить отчет по остаткам товаров"""
    products = db.query(Product).all()
    
    inventory_data = []
    low_stock_products = []
    
    for product in products:
        # Вычисляем остаток
        issued_orders = db.query(func.coalesce(func.sum(Order.qty), 0)).filter(
            Order.product_id == product.id,
            Order.status == OrderStatus.PAID_ISSUED
        ).scalar()
        
        stock = product.quantity - issued_orders
        stock = max(0, stock)
        
        # Вычисляем стоимость остатка
        stock_value = stock * (product.sell_price_rub or 0)
        
        inventory_data.append({
            'product_id': product.id,
            'product_name': product.name,
            'current_stock': stock,
            'min_stock': product.min_stock,
            'stock_value': stock_value,
            'is_low_stock': stock < product.min_stock,
            'supplier': product.supplier_name
        })
        
        if stock < product.min_stock:
            low_stock_products.append({
                'product_name': product.name,
                'current_stock': stock,
                'min_stock': product.min_stock,
                'deficit': product.min_stock - stock
            })
    
    total_stock_value = sum(item['stock_value'] for item in inventory_data)
    
    return {
        'inventory_data': inventory_data,
        'low_stock_products': low_stock_products,
        'total_stock_value': total_stock_value,
        'total_products': len(inventory_data),
        'low_stock_count': len(low_stock_products)
    }

def get_supply_report(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Получить отчет по поставкам"""
    query = db.query(Supply)
    
    if start_date:
        query = query.filter(Supply.created_at >= start_date)
    if end_date:
        query = query.filter(Supply.created_at <= end_date)
    
    supplies = query.all()
    
    # Общая статистика
    total_supplies = len(supplies)
    total_quantity = sum(supply.qty for supply in supplies)
    total_cost = sum(supply.qty * supply.buy_price_eur for supply in supplies)
    
    # Статистика по поставщикам
    supplier_stats = {}
    for supply in supplies:
        if supply.supplier_name not in supplier_stats:
            supplier_stats[supply.supplier_name] = {
                'supplier_name': supply.supplier_name,
                'supplies_count': 0,
                'total_quantity': 0,
                'total_cost': Decimal('0')
            }
        supplier_stats[supply.supplier_name]['supplies_count'] += 1
        supplier_stats[supply.supplier_name]['total_quantity'] += supply.qty
        supplier_stats[supply.supplier_name]['total_cost'] += supply.qty * supply.buy_price_eur
    
    # Добавляем среднюю стоимость для каждого поставщика
    for supplier in supplier_stats.values():
        if supplier['total_quantity'] > 0:
            supplier['avg_cost'] = supplier['total_cost'] / supplier['total_quantity']
        else:
            supplier['avg_cost'] = Decimal('0')
    
    # Статистика по товарам
    product_stats = {}
    for supply in supplies:
        if supply.product_id not in product_stats:
            product_stats[supply.product_id] = {
                'product_name': supply.product.name if supply.product else 'Неизвестный товар',
                'supplies_count': 0,
                'total_quantity': 0,
                'total_cost': Decimal('0')
            }
        product_stats[supply.product_id]['supplies_count'] += 1
        product_stats[supply.product_id]['total_quantity'] += supply.qty
        product_stats[supply.product_id]['total_cost'] += supply.qty * supply.buy_price_eur
    
    # Добавляем среднюю цену закупки для каждого товара
    for product in product_stats.values():
        if product['total_quantity'] > 0:
            product['avg_buy_price'] = product['total_cost'] / product['total_quantity']
        else:
            product['avg_buy_price'] = Decimal('0')
    
    # Добавляем product_name к поставкам
    supplies_with_names = []
    for supply in supplies:
        supply_dict = {
            'id': supply.id,
            'product_id': supply.product_id,
            'product_name': supply.product.name if supply.product else 'Неизвестный товар',
            'supplier_name': supply.supplier_name,
            'qty': supply.qty,
            'buy_price_eur': supply.buy_price_eur,
            'created_at': supply.created_at
        }
        supplies_with_names.append(supply_dict)
    
    return {
        'total_supplies': total_supplies,
        'total_quantity': total_quantity,
        'total_cost': total_cost,
        'unique_suppliers': len(supplier_stats),
        'supplier_stats': list(supplier_stats.values()),
        'product_stats': list(product_stats.values()),
        'supplies': supplies_with_names,
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    }

def get_profit_analysis(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Получить анализ прибыли"""
    # Получаем выданные заказы за период
    orders_query = db.query(Order).filter(Order.status == OrderStatus.PAID_ISSUED)
    if start_date:
        orders_query = orders_query.filter(Order.issued_at >= start_date)
    if end_date:
        orders_query = orders_query.filter(Order.issued_at <= end_date)
    
    orders = orders_query.all()
    
    # Получаем поставки за период
    supplies_query = db.query(Supply)
    if start_date:
        supplies_query = supplies_query.filter(Supply.created_at >= start_date)
    if end_date:
        supplies_query = supplies_query.filter(Supply.created_at <= end_date)
    
    supplies = supplies_query.all()
    
    # Выручка от продаж
    revenue = sum(order.qty * order.unit_price_rub for order in orders)
    
    # Себестоимость (стоимость поставок)
    cost = sum(supply.qty * supply.buy_price_eur * 100 for supply in supplies)  # Примерный курс 100 руб/евро
    
    # Прибыль
    profit = revenue - cost
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    
    # Анализ по товарам
    product_analysis = {}
    for order in orders:
        if order.product_id not in product_analysis:
            product_analysis[order.product_id] = {
                'product_name': order.product_name,
                'revenue': Decimal('0'),
                'quantity_sold': 0,
                'cost': Decimal('0'),
                'quantity_supplied': 0
            }
        product_analysis[order.product_id]['revenue'] += order.qty * order.unit_price_rub
        product_analysis[order.product_id]['quantity_sold'] += order.qty
    
    for supply in supplies:
        if supply.product_id not in product_analysis:
            product_analysis[supply.product_id] = {
                'product_name': supply.product.name if supply.product else 'Неизвестный товар',
                'revenue': Decimal('0'),
                'quantity_sold': 0,
                'cost': Decimal('0'),
                'quantity_supplied': 0
            }
        product_analysis[supply.product_id]['cost'] += supply.qty * supply.buy_price_eur * 100
        product_analysis[supply.product_id]['quantity_supplied'] += supply.qty
    
    # Вычисляем прибыль по каждому товару
    for product_data in product_analysis.values():
        product_data['profit'] = product_data['revenue'] - product_data['cost']
        product_data['profit_margin'] = (product_data['profit'] / product_data['revenue'] * 100) if product_data['revenue'] > 0 else 0
        # Добавляем среднюю цену продажи
        if product_data['quantity_sold'] > 0:
            product_data['avg_price'] = product_data['revenue'] / product_data['quantity_sold']
        else:
            product_data['avg_price'] = Decimal('0')
    
    # Разделяем товары на прибыльные и убыточные
    profitable_products = [p for p in product_analysis.values() if p['profit'] > 0]
    loss_making_products = [p for p in product_analysis.values() if p['profit'] < 0]
    
    # Сортируем по прибыли
    profitable_products.sort(key=lambda x: x['profit'], reverse=True)
    loss_making_products.sort(key=lambda x: x['profit'])
    
    return {
        'total_revenue': revenue,
        'total_cost': cost,
        'total_profit': profit,
        'profit_margin': profit_margin,
        'product_analysis': list(product_analysis.values()),
        'top_profitable_products': profitable_products[:5],  # Топ-5 прибыльных товаров
        'loss_making_products': loss_making_products[:5],   # Топ-5 убыточных товаров
        'period': {
            'start_date': start_date,
            'end_date': end_date
        }
    }

def export_sales_to_csv(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
    """Экспорт продаж в CSV"""
    query = db.query(Order).filter(Order.status == OrderStatus.PAID_ISSUED)
    
    if start_date:
        query = query.filter(Order.issued_at >= start_date)
    if end_date:
        query = query.filter(Order.issued_at <= end_date)
    
    orders = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'ID заказа', 'Дата выдачи', 'Клиент', 'Телефон', 'Товар', 
        'Количество', 'Цена за единицу (₽)', 'Общая сумма (₽)', 'Создал'
    ])
    
    # Данные
    for order in orders:
        writer.writerow([
            order.id,
            order.issued_at.strftime('%d.%m.%Y %H:%M') if order.issued_at else '',
            order.customer_name or '',
            order.phone,
            order.product_name,
            order.qty,
            float(order.unit_price_rub),
            float(order.qty * order.unit_price_rub),
            order.user_id
        ])
    
    return output.getvalue()

def export_inventory_to_csv(db: Session) -> str:
    """Экспорт остатков в CSV"""
    products = db.query(Product).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'ID товара', 'Название', 'Текущий остаток', 'Минимальный остаток', 
        'Стоимость остатка (₽)', 'Поставщик', 'Статус'
    ])
    
    # Данные
    for product in products:
        # Вычисляем остаток
        issued_orders = db.query(func.coalesce(func.sum(Order.qty), 0)).filter(
            Order.product_id == product.id,
            Order.status == OrderStatus.PAID_ISSUED
        ).scalar()
        
        stock = product.quantity - issued_orders
        stock = max(0, stock)
        stock_value = stock * (product.sell_price_rub or 0)
        status = 'Низкий остаток' if stock < product.min_stock else 'Норма'
        
        writer.writerow([
            product.id,
            product.name,
            stock,
            product.min_stock,
            float(stock_value),
            product.supplier_name or '',
            status
        ])
    
    return output.getvalue()

def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """Получить статистику для дашборда"""
    # Статистика заказов
    total_orders = db.query(func.count(Order.id)).scalar()
    pending_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PAID_NOT_ISSUED).scalar()
    issued_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatus.PAID_ISSUED).scalar()
    
    # Выручка за сегодня
    today = datetime.now().date()
    today_revenue = db.query(func.coalesce(func.sum(Order.qty * Order.unit_price_rub), 0)).filter(
        Order.status == OrderStatus.PAID_ISSUED,
        func.date(Order.issued_at) == today
    ).scalar()
    
    # Выручка за неделю
    week_ago = today - timedelta(days=7)
    week_revenue = db.query(func.coalesce(func.sum(Order.qty * Order.unit_price_rub), 0)).filter(
        Order.status == OrderStatus.PAID_ISSUED,
        Order.issued_at >= week_ago
    ).scalar()
    
    # Выручка за месяц
    month_ago = today - timedelta(days=30)
    month_revenue = db.query(func.coalesce(func.sum(Order.qty * Order.unit_price_rub), 0)).filter(
        Order.status == OrderStatus.PAID_ISSUED,
        Order.issued_at >= month_ago
    ).scalar()
    
    # Товары с низким остатком
    low_stock_count = 0
    products = db.query(Product).all()
    for product in products:
        issued_orders = db.query(func.coalesce(func.sum(Order.qty), 0)).filter(
            Order.product_id == product.id,
            Order.status == OrderStatus.PAID_ISSUED
        ).scalar()
        stock = product.quantity - issued_orders
        if stock < product.min_stock:
            low_stock_count += 1
    
    # Последние заказы
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    
    return {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'issued_orders': issued_orders,
        'today_revenue': today_revenue or Decimal('0'),
        'week_revenue': week_revenue or Decimal('0'),
        'month_revenue': month_revenue or Decimal('0'),
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders
    }
