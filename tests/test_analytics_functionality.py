import pytest
from fastapi.testclient import TestClient
from app.main import app

# Теперь используем фикстуры из conftest.py

def test_analytics_page_unauthorized(client):
    """Тест страницы аналитики без авторизации"""
    response = client.get("/admin/analytics")
    assert response.status_code == 401  # Страница защищена

def test_analytics_page_authorized(authenticated_client, test_admin):
    """Тест страницы аналитики с авторизацией"""
    response = authenticated_client.get("/admin/analytics")
    assert response.status_code == 200
    assert "Аналитика" in response.text

def test_sales_report_unauthorized(client):
    """Тест отчета по продажам без авторизации"""
    response = client.get("/admin/analytics/sales")
    assert response.status_code == 401  # Страница защищена

def test_sales_report_authorized(authenticated_client, test_admin):
    """Тест отчета по продажам с авторизацией"""
    response = authenticated_client.get("/admin/analytics/sales")
    assert response.status_code == 200
    assert "Отчет по продажам" in response.text

def test_inventory_report_unauthorized(client):
    """Тест отчета по складу без авторизации"""
    response = client.get("/admin/analytics/inventory")
    assert response.status_code == 401  # Страница защищена

def test_inventory_report_authorized(authenticated_client, test_admin):
    """Тест отчета по складу с авторизацией"""
    response = authenticated_client.get("/admin/analytics/inventory")
    assert response.status_code == 200
    assert "Остатки товаров" in response.text

def test_supply_report_unauthorized(client):
    """Тест отчета по поставкам без авторизации"""
    response = client.get("/admin/analytics/supplies")
    assert response.status_code == 401  # Страница защищена

def test_supply_report_authorized(authenticated_client, test_admin):
    """Тест отчета по поставкам с авторизацией"""
    response = authenticated_client.get("/admin/analytics/supplies")
    assert response.status_code == 200
    assert "Поставки" in response.text

def test_profit_report_unauthorized(client):
    """Тест отчета по прибыли без авторизации"""
    response = client.get("/admin/analytics/profit")
    assert response.status_code == 401  # Страница защищена

def test_profit_report_authorized(authenticated_client, test_admin):
    """Тест отчета по прибыли с авторизацией"""
    response = authenticated_client.get("/admin/analytics/profit")
    assert response.status_code == 200
    assert "Прибыль" in response.text

def test_export_sales_csv_unauthorized(client):
    """Тест экспорта продаж в CSV без авторизации"""
    response = client.get("/admin/analytics/export/sales")
    assert response.status_code == 401  # Страница защищена

def test_export_sales_csv_authorized(authenticated_client, test_admin):
    """Тест экспорта продаж в CSV с авторизацией"""
    response = authenticated_client.get("/admin/analytics/export/sales")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_export_inventory_csv_unauthorized(client):
    """Тест экспорта склада в CSV без авторизации"""
    response = client.get("/admin/analytics/export/inventory")
    assert response.status_code == 401  # Страница защищена

def test_export_inventory_csv_authorized(authenticated_client, test_admin):
    """Тест экспорта склада в CSV с авторизацией"""
    response = authenticated_client.get("/admin/analytics/export/inventory")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
