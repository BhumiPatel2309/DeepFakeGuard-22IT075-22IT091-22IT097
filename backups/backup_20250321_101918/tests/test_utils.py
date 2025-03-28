import pytest
from src.utils.utils import (
    is_valid_email,
    is_valid_username,
    is_valid_password,
    is_valid_phone
)

class TestValidation:
    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),
        ("user.name@example.co.uk", True),
        ("user+tag@example.com", True),
        ("invalid.email", False),
        ("user@.com", False),
        ("user..name@example.com", False),
        ("a" * 65 + "@example.com", False),
        ("user@" + "a" * 256 + ".com", False),
    ])
    def test_email_validation(self, email, expected):
        assert is_valid_email(email) == expected

    @pytest.mark.parametrize("username,expected", [
        ("john123", True),
        ("jane_doe", True),
        ("a_user_123", True),
        ("123user", False),
        ("_username", False),
        ("us", False),
        ("username_", False),
        ("a" * 21, False),
    ])
    def test_username_validation(self, username, expected):
        assert is_valid_username(username) == expected

    @pytest.mark.parametrize("password,expected", [
        ("StrongP@ss1", True),
        ("Weak123", False),
        ("nouppercasepass1@", False),
        ("NOLOWERCASEPASS1@", False),
        ("NoSpecialChar1", False),
        ("NoNumber@Pass", False),
        ("Short1@", False),
    ])
    def test_password_validation(self, password, expected):
        assert is_valid_password(password) == expected

    @pytest.mark.parametrize("phone,expected", [
        ("+1234567890", True),
        ("1234567890", True),
        ("+911234567890", True),
        ("123456", False),
        ("abcd1234567", False),
        ("+123" + "0" * 15, False),
    ])
    def test_phone_validation(self, phone, expected):
        assert is_valid_phone(phone) == expected
