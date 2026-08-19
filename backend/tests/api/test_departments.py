from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.application.use_cases.auth.get_current_operator import CurrentAuth
from app.domain.entities.inquiry import Inquiry
from app.domain.entities.operator import Operator, OperatorRole
from app.infrastructure.container import get_department_repository, get_object_storage
from app.infrastructure.database.memory.department_repository import InMemoryDepartmentRepository
from app.infrastructure.http.deps import require_operator
from app.infrastructure.storage.memory.storage import InMemoryStorage
from app.main import app

TINY_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
DATA_PNG = f"data:image/png;base64,{TINY_PNG}"

BODY = {
    "titulo": "3 ambientes en Palermo",
    "descripcion": "Luminoso, a 2 cuadras del subte.",
    "precio": 180000,
    "moneda": "USD",
    "metros_cuadrados": 72.5,
    "direccion": "Av. Santa Fe 3500, Palermo, CABA",
    "lat": -34.588,
    "lng": -58.411,
    "disponible": True,
    "imagenes": [],
}


def _auth() -> CurrentAuth:
    operator = Operator.create(
        email="admin@lebane.local",
        password_hash="hashed",
        role=OperatorRole.ADMIN,
    )
    return CurrentAuth(operator=operator, session_id=operator.id)


def _client() -> tuple[TestClient, InMemoryDepartmentRepository, InMemoryStorage]:
    repo = InMemoryDepartmentRepository()
    storage = InMemoryStorage()
    app.dependency_overrides[get_department_repository] = lambda: repo
    app.dependency_overrides[get_object_storage] = lambda: storage
    app.dependency_overrides[require_operator] = _auth
    return TestClient(app), repo, storage


def test_post_creates_with_202() -> None:
    client, _, _ = _client()
    try:
        response = client.post("/departamentos", json=BODY)
        assert response.status_code == 202
        data = response.json()
        assert data["titulo"] == BODY["titulo"]
        assert data["imagenes"] == []
        assert data["consultas"] == []
        assert data["id"]
    finally:
        app.dependency_overrides.clear()


def test_post_zero_price_422() -> None:
    client, _, _ = _client()
    try:
        response = client.post("/departamentos", json={**BODY, "precio": 0})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_post_invalid_currency_422() -> None:
    client, _, _ = _client()
    try:
        response = client.post("/departamentos", json={**BODY, "moneda": "EUR"})
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_post_six_images_422() -> None:
    client, _, _ = _client()
    try:
        response = client.post(
            "/departamentos", json={**BODY, "imagenes": [DATA_PNG] * 6}
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_post_invalid_image_payload_422() -> None:
    client, _, _ = _client()
    try:
        response = client.post(
            "/departamentos", json={**BODY, "imagenes": ["not-an-image"]}
        )
        assert response.status_code == 422
        assert response.json()["detail"] == (
            "Image must be an http(s) URL or an image data URL"
        )
    finally:
        app.dependency_overrides.clear()


def test_post_uploads_images_and_lists_totals() -> None:
    client, _, storage = _client()
    try:
        response = client.post(
            "/departamentos", json={**BODY, "imagenes": [DATA_PNG, DATA_PNG]}
        )
        assert response.status_code == 202
        data = response.json()
        assert len(data["imagenes"]) == 2
        assert len(storage.objects) == 2

        listed = client.get("/departamentos").json()["items"][0]
        assert listed["total_imagenes"] == 2
        assert listed["imagen_principal"] == data["imagenes"][0]

        detail = client.get(f"/departamentos/{data['id']}").json()
        assert detail["imagenes"] == data["imagenes"]
    finally:
        app.dependency_overrides.clear()


def test_get_missing_404() -> None:
    client, _, _ = _client()
    try:
        response = client.get(f"/departamentos/{uuid4()}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Department not found"
    finally:
        app.dependency_overrides.clear()


def test_put_toggles_available() -> None:
    client, _, _ = _client()
    try:
        created = client.post("/departamentos", json=BODY).json()
        response = client.put(
            f"/departamentos/{created['id']}",
            json={**BODY, "disponible": False},
        )
        assert response.status_code == 200
        assert response.json()["disponible"] is False
    finally:
        app.dependency_overrides.clear()


def test_put_replaces_images() -> None:
    client, _, storage = _client()
    try:
        created = client.post(
            "/departamentos", json={**BODY, "imagenes": [DATA_PNG]}
        ).json()
        assert len(storage.objects) == 1
        response = client.put(
            f"/departamentos/{created['id']}",
            json={**BODY, "imagenes": ["http://broken.example/x.jpg"]},
        )
        assert response.status_code == 200
        assert response.json()["imagenes"] == ["http://broken.example/x.jpg"]
        assert storage.objects == {}
    finally:
        app.dependency_overrides.clear()


def test_detail_includes_inquiries_list_only_has_count() -> None:
    client, repo, _ = _client()
    try:
        created = client.post("/departamentos", json=BODY).json()
        department = repo.get(UUID(created["id"]))
        assert department is not None
        now = datetime.now(timezone.utc)
        department.replace_inquiries(
            [
                Inquiry.create(
                    name="Ana",
                    email="ana@example.com",
                    message="¿Sigue disponible?",
                    created_at=now,
                ),
                Inquiry.create(
                    name="Beto",
                    email="beto@example.com",
                    message="¿Aceptan mascotas?",
                    created_at=now - timedelta(hours=2),
                ),
                Inquiry.create(
                    name="Cora",
                    email="cora@example.com",
                    message="Me interesa",
                    created_at=now - timedelta(days=1),
                ),
            ]
        )
        repo.update(department)

        detail = client.get(f"/departamentos/{created['id']}").json()
        assert [item["nombre"] for item in detail["consultas"]] == ["Ana", "Beto", "Cora"]
        assert detail["consultas"][0]["email"] == "ana@example.com"
        assert detail["consultas"][0]["mensaje"] == "¿Sigue disponible?"
        assert "fecha" in detail["consultas"][0]

        listed = client.get("/departamentos").json()["items"][0]
        assert listed["total_consultas"] == 3
        assert "consultas" not in listed
    finally:
        app.dependency_overrides.clear()


def test_post_inquiry_returns_201_and_updates_totals() -> None:
    client, _, _ = _client()
    try:
        created = client.post("/departamentos", json=BODY).json()
        response = client.post(
            f"/departamentos/{created['id']}/consultas",
            json={
                "nombre": "Ana Pérez",
                "email": "ana@example.com",
                "mensaje": "¿Sigue disponible?",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Ana Pérez"
        assert data["email"] == "ana@example.com"
        assert data["mensaje"] == "¿Sigue disponible?"
        assert "fecha" in data
        assert set(data) == {"nombre", "email", "mensaje", "fecha"}

        detail = client.get(f"/departamentos/{created['id']}").json()
        assert detail["consultas"][0]["nombre"] == "Ana Pérez"
        listed = client.get("/departamentos").json()["items"][0]
        assert listed["total_consultas"] == 1
    finally:
        app.dependency_overrides.clear()


def test_post_inquiry_missing_department_404() -> None:
    client, _, _ = _client()
    try:
        response = client.post(
            f"/departamentos/{uuid4()}/consultas",
            json={
                "nombre": "Ana",
                "email": "ana@example.com",
                "mensaje": "Hola",
            },
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_post_inquiry_unavailable_422() -> None:
    client, _, _ = _client()
    try:
        created = client.post(
            "/departamentos", json={**BODY, "disponible": False}
        ).json()
        response = client.post(
            f"/departamentos/{created['id']}/consultas",
            json={
                "nombre": "Ana",
                "email": "ana@example.com",
                "mensaje": "Hola",
            },
        )
        assert response.status_code == 422
        assert "available" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_post_inquiry_invalid_email_422() -> None:
    client, _, _ = _client()
    try:
        created = client.post("/departamentos", json=BODY).json()
        response = client.post(
            f"/departamentos/{created['id']}/consultas",
            json={
                "nombre": "Ana",
                "email": "no-es-email",
                "mensaje": "Hola",
            },
        )
        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
