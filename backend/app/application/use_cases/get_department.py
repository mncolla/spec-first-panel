from uuid import UUID

from app.application.exceptions import NotFoundError
from app.domain.entities.department import Department
from app.domain.repositories.department_repository import DepartmentRepository


def get_department(repo: DepartmentRepository, department_id: UUID) -> Department:
    found = repo.get(department_id)
    if found is None:
        raise NotFoundError
    return found
