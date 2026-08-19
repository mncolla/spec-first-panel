from dataclasses import dataclass
from decimal import Decimal

from app.domain.entities.department import Department
from app.domain.repositories.department_repository import DepartmentRepository


@dataclass(frozen=True)
class DepartmentPage:
    items: list[Department]
    page: int
    page_size: int
    total: int


def list_departments(
    repo: DepartmentRepository,
    *,
    page: int,
    page_size: int,
    available: bool | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_square_meters: Decimal | None = None,
    max_square_meters: Decimal | None = None,
) -> DepartmentPage:
    items, total = repo.list(
        page=page,
        page_size=page_size,
        available=available,
        min_price=min_price,
        max_price=max_price,
        min_square_meters=min_square_meters,
        max_square_meters=max_square_meters,
    )
    return DepartmentPage(items=items, page=page, page_size=page_size, total=total)
