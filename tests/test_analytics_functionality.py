import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db
from app.services.auth import get_password_hash
from app.models import User, Product, Order, Supply, OrderStatus
from decimal import Decimal
from datetime import datetime, timedelta

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analytics.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """Создает тестовую сессию БД"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """Создает тестовый клиент"""
    return TestClient(app)

@pytest.fixture(scope="function")
def test_admin(db_session):
    """Создает тестового администратора"""
    admin = User(
        username="testadmin",
        hashed_password=get_password_hash("adminpass"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    return admin

@pytest.fixture(scope="function")
def test_product(db_session):
    """Создает тестовый товар"""
    product = Product(
        name="Тестовый товар",
        description="Описание тестового товара",
        quantity=100,
        min_stock=10,
        buy_price_eur=Decimal('50.00'),
        sell_price_rub=Decimal('5000.00'),
        supplier_name="Тестовый поставщик"
    )
    db_session.add(product)
    db_session.commit()
    return product

@pytest.fixture(scope="function")
def test_order(db_session, test_product, test_admin):
    """Создает тестовый заказ"""
    order = Order(
        phone="+7 (999) 123-45-67",
        customer_name="Иван Иванов",
        product_id=test_product.id,
        product_name=test_product.name,
        qty=5,
        unit_price_rub=Decimal('5000.00'),
        status=OrderStatus.PAID_ISSUED,
        user_id=test_admin.username,
        issued_at=datetime.now()
    )
    db_session.add(order)
    db_session.commit()
    return order

@pytest.fixture(scope="function")
def test_supply(db_session, test_product):
    """Создает тестовую поставку"""
    supply = Supply(
        product_id=test_product.id,
        qty=50,
        buy_price_eur=Decimal('45.00'),
        supplier_name="Тестовый поставщик"
    )
    db_session.add(supply)
    db_session.commit()
    return supply

def test_analytics_dashboard_unauthorized(client):
    """Тест доступа к дашборду аналитики без авторизации"""
    response = client.get("/admin/analytics", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_analytics_dashboard_authorized(client, test_admin, db_session):
    """Тест доступа к дашборду аналитики с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics")
        assert response.status_code == 200
        assert "Аналитика и отчёты" in response.text
        assert "Обзор ключевых показателей" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_sales_report_unauthorized(client):
    """Тест доступа к отчету по продажам без авторизации"""
    response = client.get("/admin/analytics/sales", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_sales_report_authorized(client, test_admin, test_order, db_session):
    """Тест доступа к отчету по продажам с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics/sales")
        assert response.status_code == 200
        assert "Отчет по продажам" in response.text
        assert "Анализ продаж и выручки" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_inventory_report_unauthorized(client):
    """Тест доступа к отчету по остаткам без авторизации"""
    response = client.get("/admin/analytics/inventory", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_inventory_report_authorized(client, test_admin, test_product, db_session):
    """Тест доступа к отчету по остаткам с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics/inventory")
        assert response.status_code == 200
        assert "Остатки товаров" in response.text
        assert "Состояние склада" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_supply_report_unauthorized(client):
    """Тест доступа к отчету по поставкам без авторизации"""
    response = client.get("/admin/analytics/supplies", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_supply_report_authorized(client, test_admin, test_supply, db_session):
    """Тест доступа к отчету по поставкам с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics/supplies")
        assert response.status_code == 200
        assert "Отчет по поставкам" in response.text
        assert "Анализ поставок" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_profit_analysis_unauthorized(client):
    """Тест доступа к анализу прибыли без авторизации"""
    response = client.get("/admin/analytics/profit", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_profit_analysis_authorized(client, test_admin, test_order, test_supply, db_session):
    """Тест доступа к анализу прибыли с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics/profit")
        assert response.status_code == 200
        assert "Анализ прибыли" in response.text
        assert "Анализ рентабельности" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_export_sales_csv_unauthorized(client):
    """Тест экспорта продаж в CSV без авторизации"""
    response = client.get("/admin/analytics/export/sales", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_export_sales_csv_authorized(client, test_admin, test_order, db_session):
    """Тест экспорта продаж в CSV с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics/export/sales")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "ID заказа,Дата выдачи,Клиент,Телефон,Товар" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_export_inventory_csv_unauthorized(client):
    """Тест экспорта остатков в CSV без авторизации"""
    response = client.get("/admin/analytics/export/inventory", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_export_inventory_csv_authorized(client, test_admin, test_product, db_session):
    """Тест экспорта остатков в CSV с авторизацией"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        response = client.get("/admin/analytics/export/inventory")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "ID товара,Название,Текущий остаток,Минимальный остаток" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_sales_report_with_filters(client, test_admin, test_order, db_session):
    """Тест отчета по продажам с фильтрами"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        # Тест с фильтрами по датам
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = client.get(f"/admin/analytics/sales?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200
        assert "Отчет по продажам" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_profit_analysis_with_filters(client, test_admin, test_order, test_supply, db_session):
    """Тест анализа прибыли с фильтрами"""
    Base.metadata.create_all(bind=engine)
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })

        # Тест с фильтрами по датам
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = client.get(f"/admin/analytics/profit?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200
        assert "Анализ прибыли" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)
