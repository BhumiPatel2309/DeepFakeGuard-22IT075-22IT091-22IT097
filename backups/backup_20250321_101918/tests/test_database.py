import pytest
import sqlite3
import os
from unittest.mock import patch, MagicMock
from src.utils.database import (
    hash_password,
    init_db,
    register_user,
    login_user,
    get_db_connection
)

@pytest.fixture
def mock_db(monkeypatch):
    """Mock database connection and cursor"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    def mock_get_db():
        return mock_conn
    
    monkeypatch.setattr('src.utils.database.get_db_connection', mock_get_db)
    return mock_conn, mock_cursor

class TestDatabaseOperations:
    def test_hash_password(self):
        password = "TestPass123!"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 produces 64 character hex string
        assert hash_password(password) == hashed  # Consistent hashing

    def test_user_registration(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = None  # No existing user
        
        # Test successful registration
        success, message = register_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
            phone="+1234567890"
        )
        assert success
        assert message == "Registration successful"
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()

        # Reset mocks
        mock_conn.reset_mock()
        mock_cursor.reset_mock()
        
        # Test duplicate username
        mock_cursor.fetchone.return_value = ("existing_user",)  # Simulate existing user
        success, message = register_user(
            username="testuser",
            email="another@example.com",
            password="TestPass123!"
        )
        assert not success
        assert "already exists" in message

    def test_user_login(self, mock_db):
        mock_conn, mock_cursor = mock_db
        test_user_info = {
            "username": "logintest",
            "email": "login@example.com",
            "phone": None,
            "is_admin": 0
        }
        mock_cursor.fetchone.return_value = tuple(test_user_info.values())

        # Test successful login
        success, message, user_info = login_user("logintest", "TestPass123!")
        assert success
        assert message == "Login successful"
        assert user_info["username"] == "logintest"
        assert user_info["email"] == "login@example.com"

        # Reset mocks
        mock_cursor.reset_mock()
        mock_cursor.fetchone.return_value = None

        # Test invalid credentials
        success, message, user_info = login_user("logintest", "WrongPass123!")
        assert not success
        assert "Invalid credentials" in message
        assert user_info is None

    def test_google_auth_registration(self, mock_db):
        mock_conn, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = None  # No existing user

        success, message = register_user(
            username="googleuser",
            email="google@example.com",
            password=None,
            is_google_auth=True
        )
        assert success
        assert message == "Registration successful"
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()

    def test_google_auth_login(self, mock_db):
        mock_conn, mock_cursor = mock_db
        test_user_info = {
            "username": "googleuser",
            "email": "google@example.com",
            "phone": None,
            "is_admin": 0
        }
        mock_cursor.fetchone.return_value = tuple(test_user_info.values())

        # Test Google auth login
        success, message, user_info = login_user(
            "google@example.com",
            None,
            is_google_auth=True
        )
        assert success
        assert message == "Login successful"
        assert user_info["username"] == "googleuser"
