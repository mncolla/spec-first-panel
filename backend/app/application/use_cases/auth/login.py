from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.application.exceptions import UnauthorizedError
from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_issuer import TokenClaims, TokenIssuer
from app.domain.entities.operator import Operator
from app.domain.entities.operator_session import OperatorSession
from app.domain.repositories.operator_repository import OperatorRepository
from app.domain.repositories.session_repository import SessionRepository

SESSION_TTL = timedelta(hours=12)


@dataclass(frozen=True)
class LoginResult:
    operator: Operator
    token: str


def login(
    operators: OperatorRepository,
    sessions: SessionRepository,
    hasher: PasswordHasher,
    tokens: TokenIssuer,
    *,
    email: str,
    password: str,
) -> LoginResult:
    operator = operators.get_by_email(email.strip().lower())
    if operator is None or not hasher.verify(password, operator.password_hash):
        raise UnauthorizedError
    now = datetime.now(timezone.utc)
    session = OperatorSession(
        operator_id=operator.id,
        expires_at=now + SESSION_TTL,
        created_at=now,
    )
    sessions.add(session)
    token = tokens.issue(
        TokenClaims(
            session_id=session.id,
            operator_id=operator.id,
            role=operator.role.value,
            expires_at=session.expires_at,
        )
    )
    return LoginResult(operator=operator, token=token)
