from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.domain.entities.department import Department
from app.domain.entities.image import DepartmentImage
from app.domain.entities.inquiry import Inquiry
from app.domain.exceptions import DomainError


def _create(**overrides: object) -> Department:
    data: dict[str, object] = {
        "title": "3 ambientes en Palermo",
        "price": Decimal("180000"),
        "currency": "USD",
        "square_meters": Decimal("72.5"),
        "address": "Av. Santa Fe 3500, Palermo, CABA",
    }
    data.update(overrides)
    return Department.create(**data)  # type: ignore[arg-type]


def test_create_valid_department() -> None:
    department = _create()
    assert department.title == "3 ambientes en Palermo"
    assert department.available is True
    assert department.images == ()


def test_short_title_is_invalid() -> None:
    with pytest.raises(DomainError, match="Title"):
        _create(title="ab")


def test_zero_price_is_invalid() -> None:
    with pytest.raises(DomainError, match="Price"):
        _create(price=Decimal("0"))


def test_invalid_currency() -> None:
    with pytest.raises(DomainError, match="Currency"):
        _create(currency="EUR")


def test_non_positive_square_meters() -> None:
    with pytest.raises(DomainError, match="Square meters"):
        _create(square_meters=Decimal("0"))


def test_blank_address() -> None:
    with pytest.raises(DomainError, match="Address"):
        _create(address="   ")


def test_more_than_eight_images() -> None:
    with pytest.raises(DomainError, match="images"):
        _create(
            images=[
                DepartmentImage(url=f"http://img/{index}", position=index)
                for index in range(9)
            ]
        )


def test_seed_can_store_more_than_five_images() -> None:
    department = _create(
        images=[
            DepartmentImage(url=f"http://img/{index}", position=index)
            for index in range(8)
        ]
    )
    assert len(department.images) == 8


def test_principal_image_is_the_first() -> None:
    department = _create(
        images=[
            DepartmentImage(url="http://img/a", position=0),
            DepartmentImage(url="http://img/b", position=1),
        ]
    )
    assert department.principal_image_url == "http://img/a"
    assert len(department.images) == 2


def test_inquiries_are_ordered_by_date_desc() -> None:
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    department = _create(
        inquiries=[
            Inquiry.create(
                name="Vieja",
                email="a@x.com",
                message="primera",
                created_at=now - timedelta(days=2),
            ),
            Inquiry.create(
                name="Nueva",
                email="b@x.com",
                message="última",
                created_at=now,
            ),
        ]
    )
    assert [inquiry.name for inquiry in department.inquiries] == ["Nueva", "Vieja"]
    assert department.total_inquiries == 2


def test_add_inquiry_appends_and_orders_by_date_desc() -> None:
    now = datetime(2026, 8, 18, tzinfo=timezone.utc)
    department = _create(
        inquiries=[
            Inquiry.create(
                name="Vieja",
                email="a@x.com",
                message="primera",
                created_at=now - timedelta(days=1),
            ),
        ]
    )
    added = department.add_inquiry(
        Inquiry.create(
            name="Nueva",
            email="b@x.com",
            message="última",
            created_at=now,
        )
    )
    assert added.name == "Nueva"
    assert [inquiry.name for inquiry in department.inquiries] == ["Nueva", "Vieja"]
    assert department.total_inquiries == 2


def test_add_inquiry_rejects_unavailable_department() -> None:
    department = _create(available=False)
    with pytest.raises(DomainError, match="available"):
        department.add_inquiry(
            Inquiry.create(name="Ana", email="ana@example.com", message="Hola")
        )
