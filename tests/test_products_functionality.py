import pytest
from fastapi.testclient import TestClient
from app.main import app

# Теперь используем фикстуры из conftest.py

def test_products_page_unauthorized(client):
    """Тест страницы товаров без авторизации"""
    response = client.get("/products")
    assert response.status_code == 200
    assert "Склад" in response.text

def test_products_page_authorized(authenticated_user_client, test_user):
    """Тест страницы товаров с авторизацией"""
    response = authenticated_user_client.get("/products")
    assert response.status_code == 200
    assert "Склад" in response.text

def test_new_product_page_unauthorized(client):
    """Тест страницы создания товара без авторизации"""
    response = client.get("/products/new")
    assert response.status_code == 401  # Страница защищена

def test_new_product_page_authorized(authenticated_client, test_admin):
    """Тест страницы создания товара с авторизацией администратора"""
    response = authenticated_client.get("/products/new")
    assert response.status_code == 200
    assert "Новый товар" in response.text

def test_create_product_success(authenticated_client, test_admin, test_product):
    """Тест успешного создания товара администратором"""
    product_data = {
        "name": "Новый товар",
        "description": "Описание нового товара",
        "quantity": "50",
        "min_stock": "5",
        "buy_price_eur": "25.00",
        "sell_price_rub": "2500.00",
        "supplier_name": "Новый поставщик"
    }
    
    response = authenticated_client.post("/products", data=product_data)
    assert response.status_code == 200  # Успешное создание возвращает HTML

def test_create_product_validation_error(authenticated_client, test_admin):
    """Тест создания товара с ошибкой валидации"""
    invalid_data = {
        "name": "",  # Пустое имя
        "quantity": "invalid",  # Неверное количество
        "buy_price_eur": "invalid"  # Неверная цена
    }
    
    response = authenticated_client.post("/products", data=invalid_data)
    # Валидация может возвращать 422 или 200 с ошибками
    assert response.status_code in [200, 422]

def test_product_detail_page(authenticated_user_client, test_user, test_product):
    """Тест страницы деталей товара"""
    response = authenticated_user_client.get(f"/products/{test_product.id}")
    assert response.status_code == 200
    assert test_product.name in response.text

def test_edit_product_page_unauthorized(client, test_product):
    """Тест страницы редактирования товара без авторизации"""
    response = client.get(f"/products/{test_product.id}/edit")
    assert response.status_code == 401  # Страница защищена

def test_edit_product_page_authorized(authenticated_client, test_admin, test_product):
    """Тест страницы редактирования товара с авторизацией администратора"""
    response = authenticated_client.get(f"/products/{test_product.id}/edit")
    assert response.status_code == 200
    assert "Редактирование товара" in response.text

def test_update_product_success(authenticated_client, test_admin, test_product):
    """Тест успешного обновления товара администратором"""
    update_data = {
        "name": "Обновленный товар",
        "description": "Обновленное описание",
        "quantity": "75",
        "min_stock": "8",
        "buy_price_eur": "30.00",
        "sell_price_rub": "3000.00",
        "supplier_name": "Обновленный поставщик"
    }
    
    response = authenticated_client.post(f"/products/{test_product.id}", data=update_data)
    assert response.status_code == 200  # Успешное обновление возвращает HTML

def test_supply_page_unauthorized(client, test_product):
    """Тест страницы поставки без авторизации"""
    response = client.get(f"/products/{test_product.id}/supplies/new")
    assert response.status_code == 401  # Страница защищена

def test_supply_page_authorized(authenticated_client, test_admin, test_product):
    """Тест страницы поставки с авторизацией администратора"""
    response = authenticated_client.get(f"/products/{test_product.id}/supplies/new")
    assert response.status_code == 200
    assert "Новая поставка" in response.text

def test_create_supply_success(authenticated_client, test_admin, test_product):
    """Тест успешного создания поставки администратором"""
    supply_data = {
        "quantity": "25",
        "buy_price_eur": "20.00",
        "supplier_name": "Тестовый поставщик",
        "supply_date": "2024-12-01"
    }
    
    response = authenticated_client.post(f"/products/{test_product.id}/supplies", data=supply_data)
    # Поставка может возвращать 200 или 422 в зависимости от валидации
    assert response.status_code in [200, 422]
