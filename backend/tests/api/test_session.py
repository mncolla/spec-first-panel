from fastapi.testclient import TestClient

from app.application.use_cases.operators.bootstrap_admin import bootstrap_admin
from app.infrastructure.container import (
    get_department_repository,
    get_object_storage,
    get_operator_repository,
    get_session_repository,
)
from app.infrastructure.database.memory.department_repository import InMemoryDepartmentRepository
from app.infrastructure.database.memory.operator_repository import InMemoryOperatorRepository
from app.infrastructure.database.memory.session_repository import InMemorySessionRepository
from app.infrastructure.security.password_hasher import Pbkdf2PasswordHasher
from app.infrastructure.storage.memory.storage import InMemoryStorage
from app.main import app

ADMIN_PASSWORD = "lebanelebane"


def _client() -> tuple[TestClient, InMemoryOperatorRepository]:
    operators = InMemoryOperatorRepository()
    sessions = InMemorySessionRepository()
    bootstrap_admin(
        operators,
        Pbkdf2PasswordHasher(),
        email="admin@lebane.local",
        password=ADMIN_PASSWORD,
    )
    app.dependency_overrides[get_operator_repository] = lambda: operators
    app.dependency_overrides[get_session_repository] = lambda: sessions
    app.dependency_overrides[get_department_repository] = lambda: InMemoryDepartmentRepository()
    app.dependency_overrides[get_object_storage] = lambda: InMemoryStorage()
    return TestClient(app), operators


def _login(client: TestClient, email: str = "admin@lebane.local", password: str = ADMIN_PASSWORD) -> str:
    response = client.post("/sesion", json={"email": email, "clave": password})
    assert response.status_code == 200
    return response.json()["token"]


def test_health_is_public() -> None:
    client, _ = _client()
    try:
        assert client.get("/health").status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_departments_without_token_401() -> None:
    client, _ = _client()
    try:
        assert client.get("/departamentos").status_code == 401
        created = client.post(
            "/departamentos",
            json={
                "titulo": "3 ambientes en Palermo",
                "precio": 180000,
                "moneda": "USD",
                "metros_cuadrados": 72.5,
                "direccion": "Av. Santa Fe 3500",
            },
        )
        assert created.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_login_logout_and_revoke() -> None:
    client, _ = _client()
    try:
        token = _login(client)
        headers = {"Authorization": f"Bearer {token}"}
        me = client.get("/sesion", headers=headers)
        assert me.status_code == 200
        assert me.json() == {"email": "admin@lebane.local", "rol": "admin"}
        assert "token" not in me.json()

        listed = client.get("/departamentos", headers=headers)
        assert listed.status_code == 200

        deleted = client.delete("/sesion", headers=headers)
        assert deleted.status_code == 204
        assert client.get("/sesion", headers=headers).status_code == 401
        assert client.get("/departamentos", headers=headers).status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_login_wrong_password_401() -> None:
    client, _ = _client()
    try:
        response = client.post(
            "/sesion",
            json={"email": "admin@lebane.local", "clave": "wrong-password"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"
    finally:
        app.dependency_overrides.clear()


def test_admin_creates_agent_agent_cannot_create() -> None:
    client, _ = _client()
    try:
        admin_token = _login(client)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        created = client.post(
            "/operadores",
            headers=admin_headers,
            json={
                "email": "agente@lebane.local",
                "clave": "agentpass",
                "rol": "agente",
            },
        )
        assert created.status_code == 201
        assert created.json() == {"email": "agente@lebane.local", "rol": "agente"}

        listed = client.get("/operadores", headers=admin_headers)
        assert listed.status_code == 200
        emails = [item["email"] for item in listed.json()["items"]]
        assert emails == ["admin@lebane.local", "agente@lebane.local"]

        forbidden_role = client.post(
            "/operadores",
            headers=admin_headers,
            json={
                "email": "otro@lebane.local",
                "clave": "agentpass",
                "rol": "admin",
            },
        )
        assert forbidden_role.status_code == 422

        agent_token = _login(client, email="agente@lebane.local", password="agentpass")
        agent_headers = {"Authorization": f"Bearer {agent_token}"}
        as_agent = client.post(
            "/operadores",
            headers=agent_headers,
            json={
                "email": "tercero@lebane.local",
                "clave": "agentpass",
                "rol": "agente",
            },
        )
        assert as_agent.status_code == 403
        assert client.get("/operadores", headers=agent_headers).status_code == 403
        assert client.get("/operadores").status_code == 401
        listed = client.get("/departamentos", headers=agent_headers)
        assert listed.status_code == 200
    finally:
        app.dependency_overrides.clear()
