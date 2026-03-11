import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.core.auth import get_password_hash
from app.models.user import User

# Configurar base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas de prueba
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    """Fixture para base de datos de prueba"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    """Fixture para usuario de prueba"""
    db = TestingSessionLocal()
    
    # Crear usuario de prueba
    test_user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        role="user",
        active=True
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    db.close()
    
    return test_user

def test_register_user():
    """Test para registro de usuario"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "newpassword123",
            "role": "user"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "password" not in data

def test_register_user_duplicate_username(test_user):
    """Test para registro con username duplicado"""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",  # Usuario ya existe
            "email": "another@example.com",
            "full_name": "Another User",
            "password": "password123",
            "role": "user"
        }
    )
    
    assert response.status_code == 400
    assert "ya está en uso" in response.json()["detail"]

def test_login_user(test_user):
    """Test para login de usuario"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_invalid_credentials(test_user):
    """Test para login con credenciales inválidas"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrectos" in response.json()["detail"]

def test_get_current_user_info(test_user):
    """Test para obtener información del usuario actual"""
    # Primero hacer login para obtener token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Usar token para obtener información del usuario
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_get_current_user_info_invalid_token():
    """Test para obtener información con token inválido"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401

def test_refresh_token(test_user):
    """Test para renovar token"""
    # Primero hacer login para obtener tokens
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Renovar token
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_logout_user(test_user):
    """Test para logout de usuario"""
    # Primero hacer login para obtener token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Hacer logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "cerrada" in response.json()["message"]

def test_change_password(test_user):
    """Test para cambiar contraseña"""
    # Primero hacer login para obtener token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Cambiar contraseña
    response = client.post(
        "/api/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "testpassword",
            "new_password": "newpassword123"
        }
    )
    
    assert response.status_code == 200
    assert "cambiada" in response.json()["message"]
    
    # Verificar que se puede hacer login con la nueva contraseña
    new_login_response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "newpassword123"
        }
    )
    
    assert new_login_response.status_code == 200

