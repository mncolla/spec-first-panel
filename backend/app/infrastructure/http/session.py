from fastapi import APIRouter, Depends, Response, status

from app.application.exceptions import ForbiddenError
from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_issuer import TokenIssuer
from app.application.use_cases.auth.get_current_operator import CurrentAuth
from app.application.use_cases.auth.login import login
from app.application.use_cases.auth.logout import logout
from app.application.use_cases.operators.create_operator import create_operator
from app.application.use_cases.operators.list_operators import list_operators
from app.domain.entities.operator import OperatorRole
from app.domain.repositories.operator_repository import OperatorRepository
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.container import (
    get_hasher,
    get_operator_repository,
    get_session_repository,
    get_tokens,
)
from app.infrastructure.http.deps import require_operator
from app.infrastructure.http.schemas import (
    OperatorDetail,
    OperatorListResponse,
    OperatorWrite,
    SessionCreated,
    SessionPublic,
    SessionWrite,
)

router = APIRouter(tags=["sesion"])


@router.post("/sesion")
def create_session(
    body: SessionWrite,
    operators: OperatorRepository = Depends(get_operator_repository),
    sessions: SessionRepository = Depends(get_session_repository),
    hasher: PasswordHasher = Depends(get_hasher),
    tokens: TokenIssuer = Depends(get_tokens),
) -> SessionCreated:
    result = login(
        operators,
        sessions,
        hasher,
        tokens,
        email=body.email,
        password=body.clave,
    )
    return SessionCreated(
        email=result.operator.email,
        rol=result.operator.role.to_http(),
        token=result.token,
    )


@router.get("/sesion")
def read_session(auth: CurrentAuth = Depends(require_operator)) -> SessionPublic:
    return SessionPublic(
        email=auth.operator.email,
        rol=auth.operator.role.to_http(),
    )


@router.delete("/sesion", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    auth: CurrentAuth = Depends(require_operator),
    sessions: SessionRepository = Depends(get_session_repository),
) -> Response:
    logout(sessions, auth.session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/operadores", status_code=status.HTTP_201_CREATED)
def create_operator_item(
    body: OperatorWrite,
    auth: CurrentAuth = Depends(require_operator),
    operators: OperatorRepository = Depends(get_operator_repository),
    hasher: PasswordHasher = Depends(get_hasher),
) -> OperatorDetail:
    if auth.operator.role is not OperatorRole.ADMIN:
        raise ForbiddenError
    created = create_operator(
        operators,
        hasher,
        actor=auth.operator,
        email=body.email,
        password=body.clave,
        role=OperatorRole.from_http(body.rol),
    )
    return OperatorDetail(email=created.email, rol=created.role.to_http())


@router.get("/operadores")
def list_operator_items(
    auth: CurrentAuth = Depends(require_operator),
    operators: OperatorRepository = Depends(get_operator_repository),
) -> OperatorListResponse:
    items = list_operators(operators, actor=auth.operator)
    return OperatorListResponse(
        items=[OperatorDetail(email=item.email, rol=item.role.to_http()) for item in items]
    )
