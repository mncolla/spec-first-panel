import pytest

from app.application.exceptions import ForbiddenError, UnauthorizedError
from app.application.use_cases.auth.get_current_operator import get_current_operator
from app.application.use_cases.auth.login import login
from app.application.use_cases.auth.logout import logout
from app.application.use_cases.operators.bootstrap_admin import bootstrap_admin
from app.application.use_cases.operators.create_operator import create_operator
from app.application.use_cases.operators.list_operators import list_operators
from app.domain.entities.operator import OperatorRole
from app.domain.exceptions import DomainError
from app.infrastructure.database.memory.operator_repository import InMemoryOperatorRepository
from app.infrastructure.database.memory.session_repository import InMemorySessionRepository
from app.infrastructure.security.jwt_issuer import JwtTokenIssuer
from app.infrastructure.security.password_hasher import Pbkdf2PasswordHasher


def _stack():
    operators = InMemoryOperatorRepository()
    sessions = InMemorySessionRepository()
    hasher = Pbkdf2PasswordHasher()
    tokens = JwtTokenIssuer("test-session-secret-change-me-ok")
    admin = bootstrap_admin(
        operators, hasher, email="admin@lebane.local", password="lebanelebane"
    )
    assert admin is not None
    return operators, sessions, hasher, tokens, admin


def test_login_and_current_operator() -> None:
    operators, sessions, hasher, tokens, admin = _stack()
    result = login(
        operators,
        sessions,
        hasher,
        tokens,
        email="admin@lebane.local",
        password="lebanelebane",
    )
    assert result.operator.id == admin.id
    current = get_current_operator(operators, sessions, tokens, result.token)
    assert current.operator.email == "admin@lebane.local"


def test_login_rejects_bad_password() -> None:
    operators, sessions, hasher, tokens, _ = _stack()
    with pytest.raises(UnauthorizedError):
        login(
            operators,
            sessions,
            hasher,
            tokens,
            email="admin@lebane.local",
            password="wrong-password",
        )


def test_logout_revokes_token() -> None:
    operators, sessions, hasher, tokens, _ = _stack()
    result = login(
        operators,
        sessions,
        hasher,
        tokens,
        email="admin@lebane.local",
        password="lebanelebane",
    )
    current = get_current_operator(operators, sessions, tokens, result.token)
    logout(sessions, current.session_id)
    with pytest.raises(UnauthorizedError):
        get_current_operator(operators, sessions, tokens, result.token)


def test_create_agent_and_reject_second_admin() -> None:
    operators, _, hasher, _, admin = _stack()
    agent = create_operator(
        operators,
        hasher,
        actor=admin,
        email="agente@lebane.local",
        password="agentpass",
        role=OperatorRole.AGENT,
    )
    assert agent.role is OperatorRole.AGENT
    with pytest.raises(DomainError, match="admin"):
        create_operator(
            operators,
            hasher,
            actor=admin,
            email="otro@lebane.local",
            password="agentpass",
            role=OperatorRole.ADMIN,
        )
    with pytest.raises(ForbiddenError):
        create_operator(
            operators,
            hasher,
            actor=agent,
            email="tercero@lebane.local",
            password="agentpass",
            role=OperatorRole.AGENT,
        )


def test_list_operators_admin_only() -> None:
    operators, _, hasher, _, admin = _stack()
    create_operator(
        operators,
        hasher,
        actor=admin,
        email="agente@lebane.local",
        password="agentpass",
        role=OperatorRole.AGENT,
    )
    items = list_operators(operators, actor=admin)
    assert [item.email for item in items] == ["admin@lebane.local", "agente@lebane.local"]
    agent = next(item for item in items if item.role is OperatorRole.AGENT)
    with pytest.raises(ForbiddenError):
        list_operators(operators, actor=agent)


def test_bootstrap_is_idempotent() -> None:
    operators, _, hasher, _, _ = _stack()
    again = bootstrap_admin(
        operators, hasher, email="admin@lebane.local", password="lebanelebane"
    )
    assert again is None
