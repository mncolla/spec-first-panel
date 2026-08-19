from sqlalchemy.exc import OperationalError

from app.application.use_cases.operators.bootstrap_admin import bootstrap_admin
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.postgres.db import get_session_factory
from app.infrastructure.database.postgres.operator_repository import (
    PostgresOperatorRepository,
)
from app.infrastructure.security.password_hasher import Pbkdf2PasswordHasher


def try_bootstrap_admin() -> None:
    settings = get_settings()
    try:
        session = get_session_factory()()
    except OperationalError:
        return
    try:
        bootstrap_admin(
            PostgresOperatorRepository(session),
            Pbkdf2PasswordHasher(),
            email=settings.operator_email,
            password=settings.operator_password,
        )
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
