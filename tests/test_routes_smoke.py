#!/usr/bin/env python3
"""
Smoke-тесты для проверки основных маршрутов
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os

from app.main import app
from app.db import get_db, Base
from app.models import User, Product, Order
from app.services.auth import get_password_hash


@pytest.fixture
def test_db():
    """Создаем временную БД для тестов"""
    # Создаем временный файл БД
    fd, path = tempfile.mkstemp()
    os.close(fd)
    
    # Создаем движок для тестовой БД
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Создаем тестовые данные
    db = TestingSessionLocal()
    
    # Создаем тестового пользователя
    test_user = User(
        username="test_admin",
        hashed_password=get_password_hash("test123"),
        role="admin"
    )
    db.add(test_user)
    
    # Создаем тестовый товар
    test_product = Product(
        name="Тестовый товар",
        description="Описание тестового товара",
        min_stock=5,
        quantity=100
    )
    db.add(test_product)
    
    db.commit()
    db.close()
    
    yield path
    
    # Очищаем
    os.unlink(path)


@pytest.fixture
def client(test_db):
    """Создаем тестовый клиент"""
    def override_get_db():
        engine = create_engine(
            f"sqlite:///{test_db}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_products_new_get(client):
    """Тест GET /products/new"""
    response = client.get("/products/new")
    assert response.status_code == 200
    assert "Создание нового товара" in response.text


def test_orders_new_get(client):
    """Тест GET /orders/new"""
    response = client.get("/orders/new")
    assert response.status_code == 200
    assert "Создание нового заказа" in response.text


def test_products_new_post_success(client):
    """Тест POST /products/new с валидными данными"""
    response = client.post("/products/new", data={
        "name": "Новый товар",
        "description": "Описание",
        "min_stock": "10",
        "initial_quantity": "50"
    })
    assert response.status_code == 302  # Редирект
    assert "success" in response.headers.get("location", "")


def test_orders_new_post_success(client):
    """Тест POST /orders/new с валидными данными"""
    response = client.post("/orders", data={
        "phone": "+79001234567",
        "customer_name": "Тест Клиент",
        "product_id": "1",
        "qty": "2",
        "unit_price_rub": "1000.00",
        "eur_rate": "90.0000",
        "payment_method": "CARD"
    })
    assert response.status_code == 302  # Редирект
    assert "success" in response.headers.get("location", "")


def test_products_delete_success(client):
    """Тест POST /products/{id}/delete - успешное удаление"""
    # Сначала создаем товар
    create_response = client.post("/products", data={
        "name": "Товар для удаления",
        "description": "Описание",
        "min_stock": "5",
        "initial_quantity": "20"
    })
    assert create_response.status_code == 302
    
    # Теперь удаляем его
    response = client.post("/products/2/delete")
    assert response.status_code == 302
    assert "success" in response.headers.get("location", "")


def test_products_delete_with_orders(client):
    """Тест POST /products/{id}/delete - товар с заказами"""
    # Создаем заказ для товара
    order_response = client.post("/orders", data={
        "phone": "+79001234567",
        "customer_name": "Тест Клиент",
        "product_id": "1",
        "qty": "1",
        "unit_price_rub": "1000.00",
        "eur_rate": "90.0000",
        "payment_method": "CARD"
    })
    assert order_response.status_code == 302
    
    # Пытаемся удалить товар с заказом
    response = client.post("/products/1/delete")
    assert response.status_code == 302
    assert "error" in response.headers.get("location", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
