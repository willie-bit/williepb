from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.db.session import engine as default_engine
from app.db.session import get_db
from app.main import app


def _override_db(engine):
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def _get_db():
        with TestSession() as s:
            yield s

    return _get_db


def _client(engine):
    app.dependency_overrides[get_db] = _override_db(engine)
    return TestClient(app)


def test_register_login_me_flow(engine):
    client = _client(engine)
    try:
        r = client.post(
            "/api/v1/auth/register",
            json={
                "email": "dad@example.com",
                "password": "hunter2hunter2",
                "display_name": "아빠",
                "household_name": "Lee 가족",
            },
        )
        assert r.status_code == 201, r.text
        token = r.json()["access_token"]

        r = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 200
        me = r.json()
        assert me["email"] == "dad@example.com"
        assert me["display_name"] == "아빠"
        assert me["household_name"] == "Lee 가족"
        assert me["role"] == "OWNER"

        # Login with same credentials
        r = client.post(
            "/api/v1/auth/login",
            json={"email": "dad@example.com", "password": "hunter2hunter2"},
        )
        assert r.status_code == 200
        assert r.json()["access_token"]
    finally:
        app.dependency_overrides.clear()


def test_register_duplicate_email(engine):
    client = _client(engine)
    try:
        payload = {
            "email": "dup@example.com",
            "password": "password1234",
            "display_name": "A",
            "household_name": "H",
        }
        r1 = client.post("/api/v1/auth/register", json=payload)
        assert r1.status_code == 201
        r2 = client.post("/api/v1/auth/register", json=payload)
        assert r2.status_code == 409
    finally:
        app.dependency_overrides.clear()


def test_protected_route_requires_token(engine):
    client = _client(engine)
    try:
        r = client.get("/api/v1/dashboard")
        assert r.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_login_wrong_password(engine):
    client = _client(engine)
    try:
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "x@example.com",
                "password": "correctpassword",
                "display_name": "X",
                "household_name": "X",
            },
        )
        r = client.post(
            "/api/v1/auth/login",
            json={"email": "x@example.com", "password": "wrong"},
        )
        assert r.status_code == 401
    finally:
        app.dependency_overrides.clear()
