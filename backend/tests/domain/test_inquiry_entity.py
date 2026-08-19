from datetime import datetime, timezone

import pytest

from app.domain.entities.inquiry import Inquiry
from app.domain.exceptions import DomainError


def test_create_valid_inquiry() -> None:
    inquiry = Inquiry.create(
        name="Ana Pérez",
        email="ana@example.com",
        message="¿Sigue disponible?",
    )
    assert inquiry.name == "Ana Pérez"
    assert inquiry.email == "ana@example.com"
    assert inquiry.message == "¿Sigue disponible?"
    assert inquiry.created_at.tzinfo is not None


def test_blank_name_is_invalid() -> None:
    with pytest.raises(DomainError, match="name"):
        Inquiry.create(name="  ", email="ana@example.com", message="Hola")


def test_blank_message_is_invalid() -> None:
    with pytest.raises(DomainError, match="message"):
        Inquiry.create(name="Ana", email="ana@example.com", message="   ")


def test_invalid_email() -> None:
    with pytest.raises(DomainError, match="email"):
        Inquiry.create(name="Ana", email="not-an-email", message="Hola")


def test_created_at_can_be_set() -> None:
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    inquiry = Inquiry.create(
        name="Ana",
        email="ana@example.com",
        message="Hola",
        created_at=created,
    )
    assert inquiry.created_at == created
