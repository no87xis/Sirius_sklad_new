import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import Base, get_db
from app.services.auth import get_password_hash
from app.models import User, Product, Supply
from decimal import Decimal

# Создаем тестовую базу данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_products.db"
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

def test_create_product_page_unauthorized(client):
    """Тест страницы создания товара без авторизации"""
    response = client.get("/products/new", follow_redirects=False)
    assert response.status_code == 401  # Unauthorized

def test_create_product_page_authorized(client, test_admin):
    """Тест страницы создания товара с авторизацией"""
    # Сначала входим
    client.post("/login", data={
        "username": "testadmin",
        "password": "adminpass"
    })
    
    response = client.get("/products/new")
    assert response.status_code == 200
    assert "Новый товар" in response.text

def test_create_product_success(client, test_admin, db_session):
    """Тест успешного создания товара"""
    # Сначала входим
    client.post("/login", data={
        "username": "testadmin",
        "password": "adminpass"
    })
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        response = client.post("/products", data={
            "name": "Новый товар",
            "description": "Описание нового товара",
            "min_stock": "5",
            "buy_price_eur": "25.50",
            "sell_price_rub": "2500.00",
            "supplier_name": "Новый поставщик",
            "initial_quantity": "50"
        }, follow_redirects=False)
        
        assert response.status_code == 302  # Редирект после успешного создания
        
        # Проверяем, что товар создался в БД
        product = db_session.query(Product).filter(Product.name == "Новый товар").first()
        assert product is not None
        assert product.description == "Описание нового товара"
        assert product.quantity == 50
    finally:
        Base.metadata.drop_all(bind=engine)

def test_product_detail_page(client, test_product, db_session):
    """Тест страницы детальной информации о товаре"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        response = client.get(f"/products/{test_product.id}")
        assert response.status_code == 200
        assert test_product.name in response.text
        assert "Детальная информация о товаре" in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_edit_product_page_unauthorized(client, test_product, db_session):
    """Тест страницы редактирования товара без авторизации"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        response = client.get(f"/products/{test_product.id}/edit", follow_redirects=False)
        assert response.status_code == 401  # Unauthorized
    finally:
        Base.metadata.drop_all(bind=engine)

def test_edit_product_page_authorized(client, test_admin, test_product, db_session):
    """Тест страницы редактирования товара с авторизацией"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })
        
        response = client.get(f"/products/{test_product.id}/edit")
        assert response.status_code == 200
        assert "Редактирование товара" in response.text
        assert test_product.name in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_new_supply_page_unauthorized(client, test_product, db_session):
    """Тест страницы добавления поставки без авторизации"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        response = client.get(f"/products/{test_product.id}/supplies/new", follow_redirects=False)
        assert response.status_code == 401  # Unauthorized
    finally:
        Base.metadata.drop_all(bind=engine)

def test_new_supply_page_authorized(client, test_admin, test_product, db_session):
    """Тест страницы добавления поставки с авторизацией"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })
        
        response = client.get(f"/products/{test_product.id}/supplies/new")
        assert response.status_code == 200
        assert "Новая поставка" in response.text
        assert test_product.name in response.text
    finally:
        Base.metadata.drop_all(bind=engine)

def test_create_supply_success(client, test_admin, test_product, db_session):
    """Тест успешного создания поставки"""
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    try:
        # Сначала входим
        client.post("/login", data={
            "username": "testadmin",
            "password": "adminpass"
        })
        
        initial_quantity = test_product.quantity
        
        response = client.post(f"/products/{test_product.id}/supplies", data={
            "qty": "25",
            "supplier_name": "Тестовый поставщик",
            "buy_price_eur": "30.00"
        }, follow_redirects=False)
        
        assert response.status_code == 302  # Редирект после успешного создания
        
        # Проверяем, что поставка создалась и остаток обновился
        db_session.refresh(test_product)
        assert test_product.quantity == initial_quantity + 25
        
        supply = db_session.query(Supply).filter(Supply.product_id == test_product.id).first()
        assert supply is not None
        assert supply.qty == 25
        assert supply.buy_price_eur == Decimal('30.00')
    finally:
        Base.metadata.drop_all(bind=engine)
