import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import get_db, Base
from app.services.auth import get_password_hash
from app.models import User, Product, Order, Supply, OperationLog, PaymentMethodModel, PaymentInstrument, CashFlow, ProductPhoto, ShopCart, ShopOrder

# Глобальные переменные для тестовой БД
test_db_path = None
test_engine = None
TestingSessionLocal = None

@pytest.fixture(scope="session")
def test_db():
    """Создаем тестовую БД для всей сессии тестов"""
    global test_db_path, test_engine, TestingSessionLocal
    
    # Создаем временный файл БД
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    test_db_path = path
    
    # Создаем движок для тестовой БД
    test_engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Отключаем логирование SQL
    )
    
    # Создаем все таблицы
    Base.metadata.create_all(bind=test_engine)
    
    # Создаем фабрику сессий
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    yield path
    
    # Очищаем после всех тестов
    try:
        if test_engine:
            test_engine.dispose()
        if os.path.exists(path):
            os.unlink(path)
    except Exception as e:
        print(f"Ошибка при очистке тестовой БД: {e}")

@pytest.fixture(scope="function")
def db_session(test_db):
    """Создает сессию БД для каждого теста"""
    if not TestingSessionLocal:
        pytest.fail("Тестовая БД не инициализирована")
    
    db = TestingSessionLocal()
    try:
        # Очищаем данные перед каждым тестом
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(test_db):
    """Создает тестовый клиент с переопределенной БД"""
    def override_get_db():
        if not TestingSessionLocal:
            pytest.fail("Тестовая БД не инициализирована")
        
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
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
    db_session.refresh(user)
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
    db_session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_manager(db_session):
    """Создает тестового менеджера"""
    manager = User(
        username="testmanager",
        hashed_password=get_password_hash("managerpass"),
        role="manager"
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager

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
    db_session.refresh(product)
    return product

@pytest.fixture(scope="function")
def test_order(db_session, test_user, test_product):
    """Создает тестовый заказ"""
    order = Order(
        phone="+79001234567",
        customer_name="Тест Клиент",
        client_city="Тестовый город",
        product_id=test_product.id,
        product_name=test_product.name,
        qty=2,
        unit_price_rub=1000.0,
        eur_rate=90.0,
        order_code="TEST001",
        order_code_last4="0001",
        payment_method_id=1,
        payment_method="CARD",
        status="PAID_NOT_ISSUED",  # Используем правильный статус из enum
        user_id=test_user.username  # Используем username вместо id
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order

@pytest.fixture(scope="function")
def test_payment_method(db_session):
    """Создает тестовый метод оплаты"""
    payment_method = PaymentMethodModel(
        name="Тестовая оплата"
    )
    db_session.add(payment_method)
    db_session.commit()
    db_session.refresh(payment_method)
    return payment_method

@pytest.fixture(scope="function")
def authenticated_client(client, test_admin):
    """Создает аутентифицированный клиент"""
    # Логинимся как админ
    response = client.post("/login", data={
        "username": "testadmin",
        "password": "adminpass"
    })
    
    # Проверяем, что логин прошел (может быть 200 или 302)
    if response.status_code not in [200, 302]:
        pytest.fail(f"Ошибка аутентификации: {response.status_code}")
    
    return client

@pytest.fixture(scope="function")
def authenticated_user_client(client, test_user):
    """Создает клиент аутентифицированный как обычный пользователь"""
    # Логинимся как пользователь
    response = client.post("/login", data={
        "username": "testuser",
        "password": "testpass"
    })
    
    # Проверяем, что логин прошел (может быть 200 или 302)
    if response.status_code not in [200, 302]:
        pytest.fail(f"Ошибка аутентификации: {response.status_code}")
    
    return client
