from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.ports.object_storage import ObjectStorage
from app.domain.repositories.department_repository import DepartmentRepository
from app.infrastructure.database.postgres.db import get_session
from app.infrastructure.database.postgres.department_repository import (
    PostgresDepartmentRepository,
)
from app.infrastructure.storage.s3.storage import get_s3_storage


def get_department_repository(
    session: Session = Depends(get_session),
) -> DepartmentRepository:
    return PostgresDepartmentRepository(session)


def get_object_storage() -> ObjectStorage:
    return get_s3_storage()
