from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.ports.object_storage import ObjectStorage
from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_issuer import TokenIssuer
from app.domain.repositories.department_repository import DepartmentRepository
from app.domain.repositories.operator_repository import OperatorRepository
from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.database.postgres.db import get_session
from app.infrastructure.database.postgres.department_repository import (
    PostgresDepartmentRepository,
)
from app.infrastructure.database.postgres.operator_repository import (
    PostgresOperatorRepository,
)
from app.infrastructure.database.postgres.session_repository import (
    PostgresSessionRepository,
)
from app.infrastructure.security.jwt_issuer import get_token_issuer
from app.infrastructure.security.password_hasher import get_password_hasher
from app.infrastructure.storage.s3.storage import get_s3_storage


def get_department_repository(
    session: Session = Depends(get_session),
) -> DepartmentRepository:
    return PostgresDepartmentRepository(session)


def get_operator_repository(
    session: Session = Depends(get_session),
) -> OperatorRepository:
    return PostgresOperatorRepository(session)


def get_session_repository(
    session: Session = Depends(get_session),
) -> SessionRepository:
    return PostgresSessionRepository(session)


def get_object_storage() -> ObjectStorage:
    return get_s3_storage()


def get_hasher() -> PasswordHasher:
    return get_password_hasher()


def get_tokens() -> TokenIssuer:
    return get_token_issuer()
