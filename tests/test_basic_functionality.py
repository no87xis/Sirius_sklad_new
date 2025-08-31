import pytest
from fastapi.testclient import TestClient
from app.main import app

# Теперь используем фикстуры из conftest.py
# Все необходимые фикстуры: client, test_user, test_admin, test_product

def test_health_check(client):
    """Тест проверки здоровья API"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_main_page(client):
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Система учёта склада «Сириус»" in response.text

def test_login_page(client):
    """Тест страницы входа"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "Вход в систему" in response.text

def test_register_page(client):
    """Тест страницы регистрации"""
    response = client.get("/register")
    assert response.status_code == 200
    assert "Регистрация" in response.text

def test_products_page_unauthorized(client):
    """Тест страницы товаров без авторизации"""
    response = client.get("/products")
    assert response.status_code == 200
    assert "Управление складом" in response.text

def test_user_registration(client):
    """Тест регистрации пользователя"""
    response = client.post("/register", data={
        "username": "newuser",
        "password": "newpass",
        "confirm_password": "newpass"
    }, follow_redirects=False)
    assert response.status_code == 302  # Редирект после успешной регистрации

def test_user_login(client, test_user):
    """Тест входа пользователя"""
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    }, follow_redirects=False)
    assert response.status_code == 302  # Редирект после успешного входа

def test_user_logout(client, test_user):
    """Тест выхода пользователя"""
    # Сначала входим
    client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    
    # Затем выходим
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302

def test_analytics_page_unauthorized(client):
    """Тест страницы аналитики без авторизации - должна быть недоступна"""
    response = client.get("/admin/analytics")
    assert response.status_code == 401  # Страница защищена авторизацией

def test_analytics_page_authorized(authenticated_client, test_admin):
    """Тест страницы аналитики с авторизацией"""
    response = authenticated_client.get("/admin/analytics")
    assert response.status_code == 200
    assert "Аналитика и отчёты" in response.text
