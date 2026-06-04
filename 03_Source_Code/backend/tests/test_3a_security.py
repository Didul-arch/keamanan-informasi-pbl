import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Assuming the backend structure allows importing main app and database dependencies
from app.main import app
from database.session import Base, get_db
from database.models.user_model import UserModel
from digital_signature.encryption import encrypt_string

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import app.main as app_main

# Use a shared in-memory database URI so sync and async connections see the same data
SQLALCHEMY_DATABASE_URL_SYNC = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"
SQLALCHEMY_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL_SYNC,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

engine_async = create_async_engine(
    SQLALCHEMY_DATABASE_URL_ASYNC,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocalAsync = async_sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=engine_async)

async def override_get_db():
    async with TestingSessionLocalAsync() as db:
        yield db

# Override the database dependency to use the test database
import database.session
from unittest.mock import patch
import app.main as app_main

# Override the database dependency to use the test database
app.dependency_overrides[get_db] = override_get_db

# Patch AsyncSessionLocal globally for the duration of the tests
patcher1 = patch('app.main.AsyncSessionLocal', TestingSessionLocalAsync)
patcher2 = patch('database.session.AsyncSessionLocal', TestingSessionLocalAsync)
patcher1.start()
patcher2.start()

# Disable rate limiter for tests by mocking the limit decorator
from digital_signature.auth_router import limiter
limiter.enabled = False
limiter._enabled = False
if hasattr(app.state, "limiter"):
    app.state.limiter.enabled = False
    app.state.limiter._enabled = False

def mock_limit(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

patcher3 = patch('digital_signature.auth_router.limiter.limit', mock_limit)
patcher4 = patch('backend.app.infrastructure.config.limiter.limiter.limit', mock_limit)
try:
    patcher3.start()
except Exception:
    pass
try:
    patcher4.start()
except Exception:
    pass

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown the database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(setup_database):
    """Create a standard test user."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = TestingSessionLocal()
    hashed_password = pwd_context.hash("password123")
    from backend.app.domains.user.entity import Role
    user = UserModel(
        email="user@example.com",
        phone_number="081234567890",
        password_hash=hashed_password,
        full_name="Test User",
        is_active=True,
        role=Role.UMUM
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def admin_user(setup_database):
    """Create an admin test user."""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = TestingSessionLocal()
    hashed_password = pwd_context.hash("admin123")
    from backend.app.domains.user.entity import Role
    admin = UserModel(
        email="admin@example.com",
        phone_number="081234567891",
        password_hash=hashed_password,
        full_name="Admin User",
        is_active=True,
        role=Role.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin

@pytest.fixture
def user_token(test_user):
    """Get a valid JWT token for the standard user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_token(admin_user):
    """Get a valid JWT token for the admin user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "admin123"}
    )
    return response.json()["access_token"]

# ==========================================
# 1. AUTHENTICATION TESTS
# ==========================================

def test_auth_01_valid_login(test_user):
    """AUTH-01: Login dengan kredensial valid"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_auth_02_invalid_login(test_user):
    """AUTH-02: Login dengan password salah"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_auth_03_no_token():
    """AUTH-03: Akses API terproteksi tanpa Token"""
    response = client.get("/api/v1/history/me")
    assert response.status_code == 401

# ==========================================
# 2. CONFIDENTIALITY (ENCRYPTION) TESTS
# ==========================================

def test_auth_05_encryption_verification(setup_database):
    """AUTH-05: Enkripsi data identitas"""
    # Assuming registration flow encrypts identity
    plain_identity = "1234567890123456"
    encrypted_identity = encrypt_string(plain_identity)
    assert plain_identity != encrypted_identity
    assert type(encrypted_identity) == str

def test_auth_07_unauthorized_document_access(user_token, admin_user):
    """AUTH-07: Akses gambar KTP oleh pihak tak berwenang"""
    # Standard user trying to access admin's identity document
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/api/v1/users/{admin_user.id}/identity-document", headers=headers)
    assert response.status_code in [403, 401]

# ==========================================
# 3. AUTHORIZATION TESTS
# ==========================================

def test_auth_08_admin_access_audit_logs(admin_token):
    """AUTH-08: Akses endpoint Audit Logs oleh Admin"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_auth_10_user_bypass_audit_logs(user_token):
    """AUTH-10: Bypass Endpoint API Admin oleh User Biasa"""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/v1/admin/audit-logs", headers=headers)
    assert response.status_code == 403

def test_auth_14_illegal_claim_collection(user_token):
    """AUTH-14: Eksekusi Endpoint Klaim Ilegal"""
    # A standard user trying to mark an arbitrary claim as collected
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.patch("/api/v1/claims/999/mark-collected", headers=headers)
    # Expected 404 if claim doesn't exist, or 403 if trying to claim someone else's
    assert response.status_code in [404, 403]

# ==========================================
# 4. ACCOUNTING TESTS
# ==========================================

def test_acc_01_02_login_audit_log(setup_database):
    """ACC-01 & ACC-02: Perekaman IP saat Login Sukses & Gagal"""
    # Attempt invalid login
    client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"}
    )
    
    # We cannot strictly check the DB directly without setup, 
    # but we can verify via admin audit-logs endpoint assuming admin login works
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = TestingSessionLocal()
    from backend.app.domains.user.entity import Role
    hashed_password = pwd_context.hash("admin123")
    admin = UserModel(email="admin@example.com", full_name="Admin User", phone_number="081234567891", password_hash=hashed_password, role=Role.ADMIN, is_active=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()

    admin_login = client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "admin123"})
    admin_tok = admin_login.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {admin_tok}"}
    response = client.get("/api/v1/admin/audit-logs?limit=5", headers=headers)
    
    assert response.status_code == 200
    logs = response.json()["data"]
    
    # We should see our previous failed login attempt logged with a 401 status
    login_logs = [log for log in logs if "/login" in log["endpoint"]]
    assert len(login_logs) > 0
    # At least one should be 401 and one should be 200
    assert any(log["status_code"] == 401 for log in login_logs)
    assert any(log["status_code"] == 200 for log in login_logs)
    
def test_acc_05_audit_logs_pagination(admin_token):
    """ACC-05: Paginasi Audit Logs"""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Request explicitly limit=2
    response = client.get("/api/v1/admin/audit-logs?page=1&limit=2", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    # The length of returned logs should not exceed the limit
    assert len(data["data"]) <= 2

