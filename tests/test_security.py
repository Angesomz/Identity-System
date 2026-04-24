import pytest
from datetime import timedelta
import jwt
from ..gateway.auth import create_access_token, verify_token, settings

def test_jwt_generation_and_validation():
    """Test that JWTs are correctly generated and verified."""
    data = {"sub": "test_user", "role": "admin"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode manually to check payload
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "test_user"
    assert decoded["role"] == "admin"

def test_jwt_expiration():
    """Test that short-lived tokens expire."""
    data = {"sub": "expired_user"}
    # Create token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def test_encryption_placeholder():
    """Verify that encryption settings are loaded."""
    assert len(settings.ENCRYPTION_KEY) >= 32
