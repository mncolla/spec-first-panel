from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.application.exceptions import NotFoundError
from app.application.use_cases.create_department import create_department
from app.application.use_cases.create_inquiry import create_inquiry
from app.application.use_cases.list_departments import list_departments
from app.domain.entities.inquiry import Inquiry
from app.domain.exceptions import DomainError
from app.infrastructure.database.memory.department_repository import InMemoryDepartmentRepository
from app.infrastructure.storage.memory.storage import InMemoryStorage


def _create_department(repo, **overrides: object):
    data = {
        "title": "3 ambientes en Palermo",
        "price": Decimal("180000"),
        "currency": "USD",
        "square_meters": Decimal("72.5"),
        "address": "Av. Santa Fe 3500, Palermo, CABA",
    }
    data.update(overrides)
    return create_department(repo, InMemoryStorage(), **data)  # type: ignore[arg-type]


def test_create_inquiry_persists_and_counts_on_list() -> None:
    repo = InMemoryDepartmentRepository()
    department = _create_department(repo)
    now = datetime.now(timezone.utc)
    department.replace_inquiries(
        [
            Inquiry.create(
                name="Vieja",
                email="old@example.com",
                message="primera",
                created_at=now - timedelta(hours=1),
            )
        ]
    )
    repo.update(department)

    created = create_inquiry(
        repo,
        department.id,
        name="Ana Pérez",
        email="ana@example.com",
        message="¿Sigue disponible?",
    )

    assert created.name == "Ana Pérez"
    fetched = repo.get(department.id)
    assert fetched is not None
    assert [inquiry.name for inquiry in fetched.inquiries] == ["Ana Pérez", "Vieja"]

    page = list_departments(repo, page=1, page_size=10)
    assert page.items[0].total_inquiries == 2


def test_create_inquiry_missing_department() -> None:
    repo = InMemoryDepartmentRepository()
    with pytest.raises(NotFoundError):
        create_inquiry(
            repo,
            uuid4(),
            name="Ana",
            email="ana@example.com",
            message="Hola",
        )


def test_create_inquiry_rejects_unavailable() -> None:
    repo = InMemoryDepartmentRepository()
    department = _create_department(repo, available=False)
    with pytest.raises(DomainError, match="available"):
        create_inquiry(
            repo,
            department.id,
            name="Ana",
            email="ana@example.com",
            message="Hola",
        )
