from typing import Annotated

from fastapi import Depends, Header

from app.application.exceptions import UnauthorizedError
from app.application.ports.token_issuer import TokenIssuer
from app.application.use_cases.auth.get_current_operator import CurrentAuth, get_current_operator
from app.domain.repositories.operator_repository import OperatorRepository
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.container import (
    get_operator_repository,
    get_session_repository,
    get_tokens,
)


def require_operator(
    authorization: Annotated[str | None, Header()] = None,
    operators: OperatorRepository = Depends(get_operator_repository),
    sessions: SessionRepository = Depends(get_session_repository),
    tokens: TokenIssuer = Depends(get_tokens),
) -> CurrentAuth:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise UnauthorizedError
    return get_current_operator(operators, sessions, tokens, token)
