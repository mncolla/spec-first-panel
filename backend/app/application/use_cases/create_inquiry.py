from uuid import UUID

from app.application.exceptions import NotFoundError
from app.domain.entities.inquiry import Inquiry
from app.domain.repositories.department_repository import DepartmentRepository


def create_inquiry(
    repo: DepartmentRepository,
    department_id: UUID,
    *,
    name: str,
    email: str,
    message: str,
) -> Inquiry:
    department = repo.get(department_id)
    if department is None:
        raise NotFoundError
    inquiry = Inquiry.create(name=name, email=email, message=message)
    department.add_inquiry(inquiry)
    repo.update(department)
    return inquiry
