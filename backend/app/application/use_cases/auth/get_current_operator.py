from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.application.exceptions import UnauthorizedError
from app.application.ports.token_issuer import TokenIssuer
from app.domain.entities.operator import Operator
from app.domain.repositories.operator_repository import OperatorRepository
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class CurrentAuth:
    operator: Operator
    session_id: UUID


def get_current_operator(
    operators: OperatorRepository,
    sessions: SessionRepository,
    tokens: TokenIssuer,
    token: str,
) -> CurrentAuth:
    claims = tokens.parse(token)
    if claims is None:
        raise UnauthorizedError
    session = sessions.get(claims.session_id)
    if session is None or session.is_expired(datetime.now(timezone.utc)):
        raise UnauthorizedError
    if session.operator_id != claims.operator_id:
        raise UnauthorizedError
    operator = operators.get(claims.operator_id)
    if operator is None:
        raise UnauthorizedError
    return CurrentAuth(operator=operator, session_id=session.id)
