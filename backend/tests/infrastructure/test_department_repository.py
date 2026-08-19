from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from sqlalchemy import delete
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.domain.entities.department import Department
from app.domain.entities.image import DepartmentImage
from app.domain.entities.inquiry import Inquiry
from app.infrastructure.database.postgres.db import get_engine
from app.infrastructure.database.postgres.department_repository import (
    PostgresDepartmentRepository,
)
from app.infrastructure.database.postgres.models import DepartmentModel


def _alembic_upgrade() -> None:
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    command.upgrade(config, "head")


def _create(**overrides: object) -> Department:
    data: dict[str, object] = {
        "title": "Test department",
        "price": Decimal("150000"),
        "currency": "USD",
        "square_meters": Decimal("50"),
        "address": "Calle Falsa 123",
    }
    data.update(overrides)
    return Department.create(**data)  # type: ignore[arg-type]


@pytest.fixture
def session() -> Session:
    try:
        engine = get_engine()
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except OperationalError:
        pytest.skip("Postgres is not available")

    _alembic_upgrade()
    # Isolate each test in a rolled-back transaction so we never wipe the
    # Compose seed. DELETE stays inside this transaction.
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint")
    db.execute(delete(DepartmentModel))
    db.flush()
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


def test_list_filters_by_min_price(session: Session) -> None:
    repo = PostgresDepartmentRepository(session)
    repo.add(_create(title="Cheap", price=Decimal("80000")))
    repo.add(_create(title="Expensive", price=Decimal("200000")))
    session.flush()

    items, total = repo.list(page=1, page_size=10, min_price=Decimal("100000"))
    titles = {item.title for item in items}
    assert total == 1
    assert titles == {"Expensive"}


def test_list_filters_availability_and_pagination(session: Session) -> None:
    repo = PostgresDepartmentRepository(session)
    repo.add(_create(title="Active", available=True))
    repo.add(_create(title="Off", available=False))
    session.flush()

    items, total = repo.list(page=1, page_size=10, available=True)
    assert total == 1
    assert items[0].title == "Active"

    empty, real_total = repo.list(page=9, page_size=10)
    assert empty == []
    assert real_total == 2


def test_get_missing_returns_none(session: Session) -> None:
    repo = PostgresDepartmentRepository(session)
    assert repo.get(uuid4()) is None


def test_persists_images_and_list_totals(session: Session) -> None:
    repo = PostgresDepartmentRepository(session)
    department = _create(
        images=[
            DepartmentImage(url="http://img/principal", position=0, storage_key="a"),
            DepartmentImage(url="http://img/second", position=1, storage_key="b"),
        ]
    )
    repo.add(department)
    session.flush()

    fetched = repo.get(department.id)
    assert fetched is not None
    assert [image.url for image in fetched.images] == [
        "http://img/principal",
        "http://img/second",
    ]

    items, total = repo.list(page=1, page_size=10)
    assert total == 1
    assert items[0].principal_image_url == "http://img/principal"
    assert len(items[0].images) == 2


def test_persists_inquiries_on_detail_and_count_on_list(session: Session) -> None:
    repo = PostgresDepartmentRepository(session)
    now = datetime.now(timezone.utc)
    department = _create(
        inquiries=[
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
                created_at=now - timedelta(hours=1),
            ),
            Inquiry.create(
                name="Cora",
                email="cora@example.com",
                message="Me interesa",
                created_at=now - timedelta(days=1),
            ),
        ]
    )
    repo.add(department)
    session.flush()

    fetched = repo.get(department.id)
    assert fetched is not None
    assert [inquiry.name for inquiry in fetched.inquiries] == ["Ana", "Beto", "Cora"]
    assert fetched.total_inquiries == 3

    items, total = repo.list(page=1, page_size=10)
    assert total == 1
    assert items[0].inquiries == ()
    assert items[0].total_inquiries == 3


def test_update_persists_added_inquiry(session: Session) -> None:
    repo = PostgresDepartmentRepository(session)
    department = _create()
    repo.add(department)
    session.flush()

    fetched = repo.get(department.id)
    assert fetched is not None
    fetched.add_inquiry(
        Inquiry.create(name="Ana", email="ana@example.com", message="Me interesa")
    )
    repo.update(fetched)
    session.flush()

    reloaded = repo.get(department.id)
    assert reloaded is not None
    assert [inquiry.name for inquiry in reloaded.inquiries] == ["Ana"]
    assert reloaded.total_inquiries == 1

    items, _ = repo.list(page=1, page_size=10)
    assert items[0].inquiries == ()
    assert items[0].total_inquiries == 1
