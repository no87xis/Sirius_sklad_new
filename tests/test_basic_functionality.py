import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db
from app.services.auth import get_password_hash
from app.models import User, Product, Supply

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
def test_user(db_session):
    """Создает тестового пользователя"""
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    return user

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
        buy_price_eur=50.0,
        sell_price_rub=5000.0,
        supplier_name="Тестовый поставщик"
    )
    db_session.add(product)
    db_session.commit()
    return product

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

def test_products_page_unauthorized(client, db_session):
    """Тест страницы товаров без авторизации"""
    # Создаем таблицы для этого теста
    Base.metadata.create_all(bind=engine)
    try:
        response = client.get("/products")
        assert response.status_code == 200
        assert "Управление складом" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_user_registration(client, db_session):
    """Тест регистрации пользователя"""
    # Создаем таблицы для этого теста
    Base.metadata.create_all(bind=engine)
    try:
        response = client.post("/register", data={
            "username": "newuser",
            "password": "newpass",
            "confirm_password": "newpass"
        }, follow_redirects=False)
        assert response.status_code == 302  # Редирект после успешной регистрации
    finally:
        Base.metadata.drop_all(bind=engine)

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
    """Тест страницы аналитики без авторизации"""
    response = client.get("/admin/analytics")
    assert response.status_code == 200
    assert "Аналитика и отчёты" in response.text
