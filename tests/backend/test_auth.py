import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, verify_access_token


def test_password_hashing():
    raw_password = "SecretPassword123"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = create_access_token({"sub": user_id})
    assert isinstance(token, str)

    extracted = verify_access_token(token)
    assert extracted == user_id
