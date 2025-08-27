import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.models import User, UserRole, OperationLog
from app.services.auth import get_password_hash

# Импортируем фикстуры из других тестов
from tests.test_basic_functionality import db_session

@pytest.fixture
def client():
    """Создает тестовый клиент"""
    return TestClient(app)

@pytest.fixture
def admin_user(db_session: Session):
    """Создает пользователя-админа для тестов"""
    user = User(
        username="admin_test",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def manager_user(db_session: Session):
    """Создает пользователя-менеджера для тестов"""
    user = User(
        username="manager_test",
        hashed_password=get_password_hash("manager123"),
        role=UserRole.MANAGER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def regular_user(db_session: Session):
    """Создает обычного пользователя для тестов"""
    user = User(
        username="user_test",
        hashed_password=get_password_hash("user123"),
        role=UserRole.USER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_logs(db_session: Session, admin_user, manager_user):
    """Создает тестовые логи"""
    logs = [
        OperationLog(
            user_id=admin_user.username,
            action="user_create",
            entity_type="user",
            entity_id="test_user",
            details="Создан пользователь test_user"
        ),
        OperationLog(
            user_id=manager_user.username,
            action="product_create",
            entity_type="product",
            entity_id="1",
            details="Создан товар Test Product"
        ),
        OperationLog(
            user_id=admin_user.username,
            action="order_create",
            entity_type="order",
            entity_id="123",
            details="Создан заказ #123"
        )
    ]
    for log in logs:
        db_session.add(log)
    db_session.commit()
    return logs

class TestAdminDashboard:
    """Тесты для админ-дашборда"""
    
    def test_admin_dashboard_unauthorized(self, db_session: Session, client):
        """Тест доступа к дашборду без авторизации"""
        response = client.get("/admin")
        assert response.status_code == 401
    
    def test_admin_dashboard_authorized(self, db_session: Session, admin_user, client):
        """Тест доступа к дашборду с правами админа"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Доступ к дашборду
        response = client.get("/admin")
        assert response.status_code == 200
        assert "Админ-панель" in response.text
        assert "Статистика пользователей" in response.text
        assert "Статистика логов" in response.text
    
    def test_admin_dashboard_manager_access(self, db_session: Session, manager_user, client):
        """Тест доступа к дашборду с правами менеджера"""
        # Авторизация
        response = client.post("/login", data={
            "username": "manager_test",
            "password": "manager123"
        })
        assert response.status_code == 200
        
        # Доступ к дашборду (должен быть запрещен)
        response = client.get("/admin")
        assert response.status_code == 403

class TestUserManagement:
    """Тесты для управления пользователями"""
    
    def test_users_list_unauthorized(self, db_session: Session, client):
        """Тест доступа к списку пользователей без авторизации"""
        response = client.get("/admin/users")
        assert response.status_code == 401
    
    def test_users_list_authorized(self, db_session: Session, admin_user, manager_user, regular_user, client):
        """Тест доступа к списку пользователей с правами админа"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Доступ к списку пользователей
        response = client.get("/admin/users")
        assert response.status_code == 200
        assert "Управление пользователями" in response.text
        assert "admin_test" in response.text
        assert "manager_test" in response.text
        assert "user_test" in response.text
    
    def test_create_user_form(self, db_session: Session, admin_user, client):
        """Тест формы создания пользователя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Доступ к форме создания
        response = client.get("/admin/users/new")
        assert response.status_code == 200
        assert "Новый пользователь" in response.text
        assert "username" in response.text
        assert "password" in response.text
        assert "role" in response.text
    
    def test_create_user_success(self, db_session: Session, admin_user, client):
        """Тест успешного создания пользователя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Создание пользователя
        response = client.post("/admin/users", data={
            "username": "new_user",
            "password": "newpass123",
            "role": "USER"
        })
        assert response.status_code == 200
        
        # Проверка создания в БД
        user = db_session.query(User).filter(User.username == "new_user").first()
        assert user is not None
        assert user.role == UserRole.USER
    
    def test_create_user_duplicate_username(self, db_session: Session, admin_user, regular_user, client):
        """Тест создания пользователя с существующим именем"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Попытка создания пользователя с существующим именем
        response = client.post("/admin/users", data={
            "username": "user_test",  # Уже существует
            "password": "newpass123",
            "role": "USER"
        })
        assert response.status_code == 400
        assert "уже существует" in response.text
    
    def test_user_detail(self, db_session: Session, admin_user, regular_user, client):
        """Тест просмотра деталей пользователя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Просмотр деталей пользователя
        response = client.get(f"/admin/users/{regular_user.username}")
        assert response.status_code == 200
        assert "user_test" in response.text
        assert "user" in response.text
    
    def test_user_edit_form(self, db_session: Session, admin_user, regular_user, client):
        """Тест формы редактирования пользователя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Доступ к форме редактирования
        response = client.get(f"/admin/users/{regular_user.username}/edit")
        assert response.status_code == 200
        assert "Редактирование" in response.text
        assert "user_test" in response.text
    
    def test_update_user_success(self, db_session: Session, admin_user, regular_user, client):
        """Тест успешного обновления пользователя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Обновление пользователя
        response = client.post(f"/admin/users/{regular_user.username}", data={
            "username": "updated_user",
            "role": "MANAGER"
        })
        assert response.status_code == 200
        
        # Проверка обновления в БД
        db_session.refresh(regular_user)
        assert regular_user.username == "updated_user"
        assert regular_user.role == UserRole.MANAGER
    
    def test_delete_user_success(self, db_session: Session, admin_user, regular_user, client):
        """Тест успешного удаления пользователя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Удаление пользователя
        response = client.post(f"/admin/users/{regular_user.username}/delete")
        assert response.status_code == 200
        
        # Проверка удаления из БД
        user = db_session.query(User).filter(User.username == regular_user.username).first()
        assert user is None
    
    def test_delete_self_forbidden(self, db_session: Session, admin_user, client):
        """Тест запрета удаления самого себя"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Попытка удаления самого себя
        response = client.post(f"/admin/users/{admin_user.username}/delete")
        assert response.status_code == 400
        assert "нельзя удалить" in response.text

class TestOperationLogs:
    """Тесты для логов операций"""
    
    def test_logs_unauthorized(self, db_session: Session, client):
        """Тест доступа к логам без авторизации"""
        response = client.get("/admin/logs")
        assert response.status_code == 401
    
    def test_logs_authorized(self, db_session: Session, admin_user, test_logs, client):
        """Тест доступа к логам с правами админа"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Доступ к логам
        response = client.get("/admin/logs")
        assert response.status_code == 200
        assert "Логи операций" in response.text
        assert "admin_test" in response.text
        assert "manager_test" in response.text
        assert "user_create" in response.text
        assert "product_create" in response.text
    
    def test_logs_with_filters(self, db_session: Session, admin_user, test_logs, client):
        """Тест фильтрации логов"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Фильтрация по типу операции
        response = client.get("/admin/logs?operation_type=user_create")
        assert response.status_code == 200
        assert "user_create" in response.text
        assert "product_create" not in response.text
        
        # Фильтрация по пользователю
        response = client.get("/admin/logs?user_id=admin_test")
        assert response.status_code == 200
        assert "admin_test" in response.text
        assert "manager_test" not in response.text
    
    def test_logs_statistics(self, db_session: Session, admin_user, test_logs, client):
        """Тест статистики логов"""
        # Авторизация
        response = client.post("/login", data={
            "username": "admin_test",
            "password": "admin123"
        })
        assert response.status_code == 200
        
        # Проверка статистики
        response = client.get("/admin/logs")
        assert response.status_code == 200
        assert "3" in response.text  # Общее количество логов
        assert "2" in response.text  # Логи за неделю (примерно)
        assert "2" in response.text  # Количество активных пользователей
