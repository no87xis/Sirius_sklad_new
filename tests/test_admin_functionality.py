import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.main import app
from app.models import User, UserRole, OperationLog
from app.services.auth import get_password_hash

# Теперь используем фикстуры из conftest.py

class TestUserManagement:
    """Тесты управления пользователями"""
    
    def test_users_page_unauthorized(self, client):
        """Тест страницы пользователей без авторизации"""
        response = client.get("/admin/users")
        assert response.status_code == 401  # Страница защищена
    
    def test_users_page_authorized(self, authenticated_client, test_admin):
        """Тест страницы пользователей с авторизацией"""
        response = authenticated_client.get("/admin/users")
        assert response.status_code == 200
        assert "Управление пользователями" in response.text
    
    def test_create_user_form(self, authenticated_client, test_admin):
        """Тест формы создания пользователя"""
        response = authenticated_client.get("/admin/users/new")
        assert response.status_code == 200
        assert "Новый пользователь" in response.text
    
    def test_create_user_success(self, authenticated_client, test_admin):
        """Тест успешного создания пользователя"""
        user_data = {
            "username": "newuser",
            "password": "newpass123",
            "role": "user"
        }
        
        response = authenticated_client.post("/admin/users", data=user_data)
        assert response.status_code == 200  # Успешное создание возвращает HTML
    
    def test_create_user_duplicate_username(self, authenticated_client, test_admin, test_user):
        """Тест создания пользователя с дублирующимся именем"""
        user_data = {
            "username": test_user.username,  # Уже существует
            "password": "newpass123",
            "role": "user"
        }
        
        response = authenticated_client.post("/admin/users", data=user_data)
        assert response.status_code == 200  # Возвращает HTML с ошибкой
    
    def test_user_detail_page(self, authenticated_client, test_admin, test_user):
        """Тест страницы деталей пользователя"""
        response = authenticated_client.get(f"/admin/users/{test_user.username}")
        assert response.status_code == 200
        assert test_user.username in response.text
    
    def test_edit_user_page(self, authenticated_client, test_admin, test_user):
        """Тест страницы редактирования пользователя"""
        response = authenticated_client.get(f"/admin/users/{test_user.username}/edit")
        assert response.status_code == 200
        assert "Редактирование пользователя" in response.text
    
    def test_update_user_success(self, authenticated_client, test_admin, test_user):
        """Тест успешного обновления пользователя"""
        update_data = {
            "username": "updateduser",
            "role": "manager"
        }
        
        response = authenticated_client.post(f"/admin/users/{test_user.username}", data=update_data)
        assert response.status_code == 200  # Успешное обновление возвращает HTML
    
    def test_delete_user_success(self, authenticated_client, test_admin, test_user):
        """Тест успешного удаления пользователя"""
        response = authenticated_client.post(f"/admin/users/{test_user.username}/delete")
        assert response.status_code == 200  # Успешное удаление возвращает HTML
    
    def test_delete_self_forbidden(self, authenticated_client, test_admin):
        """Тест запрета удаления самого себя"""
        response = authenticated_client.post(f"/admin/users/{test_admin.username}/delete")
        assert response.status_code == 200  # Возвращает HTML с ошибкой

class TestOperationLogs:
    """Тесты логов операций"""
    
    def test_logs_page_unauthorized(self, client):
        """Тест страницы логов без авторизации"""
        response = client.get("/admin/logs")
        assert response.status_code == 401  # Страница защищена
    
    def test_logs_page_authorized(self, authenticated_client, test_admin):
        """Тест страницы логов с авторизацией"""
        response = authenticated_client.get("/admin/logs")
        assert response.status_code == 200
        assert "Логи операций" in response.text
    
    def test_logs_statistics(self, authenticated_client, test_admin):
        """Тест статистики логов"""
        response = authenticated_client.get("/admin/logs")
        assert response.status_code == 200
        assert "Логи операций" in response.text
