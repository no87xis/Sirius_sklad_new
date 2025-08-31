import pytest
from fastapi.testclient import TestClient
from app.main import app

# Теперь используем фикстуры из conftest.py
# Все необходимые фикстуры: client, test_user, test_admin, test_product, test_order, test_payment_method

def test_orders_page_unauthorized(client):
    """Тест страницы заказов без авторизации"""
    response = client.get("/orders")
    assert response.status_code == 200
    assert "Заказы" in response.text

def test_orders_page_authorized(authenticated_user_client, test_user):
    """Тест страницы заказов с авторизацией"""
    response = authenticated_user_client.get("/orders")
    assert response.status_code == 200
    assert "Заказы" in response.text

def test_new_order_page_unauthorized(client):
    """Тест страницы создания заказа без авторизации"""
    response = client.get("/orders/new")
    assert response.status_code == 401  # Страница защищена

def test_new_order_page_authorized(authenticated_user_client, test_user):
    """Тест страницы создания заказа с авторизацией"""
    response = authenticated_user_client.get("/orders/new")
    assert response.status_code == 200
    assert "Новый заказ" in response.text

def test_create_order_success(authenticated_user_client, test_user, test_product):
    """Тест успешного создания заказа"""
    order_data = {
        "phone": "+79001234567",
        "customer_name": "Тест Клиент",
        "client_city": "Тестовый город",
        "product_id": str(test_product.id),
        "qty": "2",
        "unit_price_rub": "1000.00",
        "eur_rate": "90.0000",
        "payment_method": "CARD"
    }
    
    response = authenticated_user_client.post("/orders", data=order_data)
    assert response.status_code == 200  # Успешное создание возвращает HTML

def test_order_detail_page(authenticated_user_client, test_user, test_order):
    """Тест страницы деталей заказа"""
    response = authenticated_user_client.get(f"/orders/{test_order.id}")
    assert response.status_code == 200
    assert test_order.customer_name in response.text

def test_edit_order_page_unauthorized(client, test_order):
    """Тест страницы редактирования заказа без авторизации"""
    response = client.get(f"/orders/{test_order.id}/edit")
    assert response.status_code == 401  # Страница защищена

def test_edit_order_page_authorized(authenticated_client, test_admin, test_order):
    """Тест страницы редактирования заказа с авторизацией"""
    response = authenticated_client.get(f"/orders/{test_order.id}/edit")
    assert response.status_code == 200
    assert "Редактирование заказа" in response.text

def test_update_order_status(authenticated_client, test_admin, test_order):
    """Тест обновления статуса заказа"""
    new_status = "paid"
    response = authenticated_client.post(f"/orders/{test_order.id}/status", data={
        "status": new_status
    })
    assert response.status_code == 200  # Успешное обновление возвращает HTML

def test_search_orders_page(authenticated_user_client, test_user, test_order):
    """Тест страницы поиска заказов"""
    response = authenticated_user_client.get("/orders/search?phone=+79001234567")
    assert response.status_code == 200
    assert "Поиск заказов" in response.text
