from decimal import Decimal
from uuid import uuid4

import pytest

from app.application.exceptions import NotFoundError
from app.application.image_input import ImageInput, parse_image_write
from app.application.use_cases.create_department import create_department
from app.application.use_cases.get_department import get_department
from app.application.use_cases.list_departments import list_departments
from app.application.use_cases.update_department import update_department
from app.domain.exceptions import DomainError
from app.infrastructure.database.memory.department_repository import InMemoryDepartmentRepository
from app.infrastructure.storage.memory.storage import InMemoryStorage

TINY_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
DATA_PNG = f"data:image/png;base64,{TINY_PNG}"


def _create(repo, storage, **overrides: object):
    data = {
        "title": "3 ambientes en Palermo",
        "price": Decimal("180000"),
        "currency": "USD",
        "square_meters": Decimal("72.5"),
        "address": "Av. Santa Fe 3500, Palermo, CABA",
    }
    data.update(overrides)
    return create_department(repo, storage, **data)  # type: ignore[arg-type]


def test_create_department_can_be_fetched() -> None:
    repo = InMemoryDepartmentRepository()
    storage = InMemoryStorage()
    created = _create(repo, storage)
    fetched = get_department(repo, created.id)
    assert fetched.id == created.id
    assert fetched.title == "3 ambientes en Palermo"
    assert fetched.images == ()


def test_create_uploads_images_and_exposes_totals() -> None:
    repo = InMemoryDepartmentRepository()
    storage = InMemoryStorage()
    payload = parse_image_write(DATA_PNG)
    created = _create(repo, storage, images=[payload, payload])

    assert len(storage.objects) == 2
    assert len(created.images) == 2
    assert created.principal_image_url is not None
    assert created.principal_image_url.startswith("https://memory.local/")

    page = list_departments(repo, page=1, page_size=10)
    assert page.items[0].principal_image_url == created.principal_image_url
    assert len(page.items[0].images) == 2


def test_create_rejects_more_than_five_images() -> None:
    repo = InMemoryDepartmentRepository()
    storage = InMemoryStorage()
    payload = parse_image_write(DATA_PNG)
    with pytest.raises(DomainError, match="images"):
        _create(repo, storage, images=[payload] * 6)


def test_get_missing_department() -> None:
    repo = InMemoryDepartmentRepository()
    with pytest.raises(NotFoundError):
        get_department(repo, uuid4())


def test_update_replaces_image_set() -> None:
    repo = InMemoryDepartmentRepository()
    storage = InMemoryStorage()
    created = _create(repo, storage, images=[parse_image_write(DATA_PNG)])
    old_key = created.images[0].storage_key
    assert old_key in storage.objects

    updated = update_department(
        repo,
        storage,
        created.id,
        title=created.title,
        price=created.price,
        currency=created.currency.value,
        square_meters=created.square_meters,
        address=created.address,
        description=created.description,
        lat=created.lat,
        lng=created.lng,
        available=created.available,
        images=[ImageInput(url="http://broken.example/missing.jpg")],
    )
    assert [image.url for image in updated.images] == [
        "http://broken.example/missing.jpg"
    ]
    assert old_key in storage.deleted
    assert old_key not in storage.objects
