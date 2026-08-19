import pytest

from app.domain.entities.operator import Operator, OperatorRole
from app.domain.exceptions import DomainError


def test_create_admin() -> None:
    operator = Operator.create(
        email="Admin@lebane.local",
        password_hash="hashed",
        role=OperatorRole.ADMIN,
    )
    assert operator.email == "admin@lebane.local"
    assert operator.role is OperatorRole.ADMIN
    assert operator.role.to_http() == "admin"


def test_agent_http_role() -> None:
    assert OperatorRole.AGENT.to_http() == "agente"
    assert OperatorRole.from_http("agente") is OperatorRole.AGENT


def test_invalid_email() -> None:
    with pytest.raises(DomainError, match="email"):
        Operator.create(email="not-an-email", password_hash="x", role=OperatorRole.AGENT)


def test_blank_password_hash() -> None:
    with pytest.raises(DomainError, match="hash"):
        Operator.create(email="a@b.com", password_hash="", role=OperatorRole.AGENT)
