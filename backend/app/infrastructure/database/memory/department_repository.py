from decimal import Decimal
from uuid import UUID

from app.domain.entities.department import Department


class InMemoryDepartmentRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Department] = {}

    def add(self, department: Department) -> Department:
        self._items[department.id] = department
        return department

    def get(self, department_id: UUID) -> Department | None:
        return self._items.get(department_id)

    def update(self, department: Department) -> Department:
        self._items[department.id] = department
        return department

    def list(
        self,
        *,
        page: int,
        page_size: int,
        available: bool | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        min_square_meters: Decimal | None = None,
        max_square_meters: Decimal | None = None,
    ) -> tuple[list[Department], int]:
        items = list(self._items.values())
        if available is not None:
            items = [item for item in items if item.available is available]
        if min_price is not None:
            items = [item for item in items if item.price >= min_price]
        if max_price is not None:
            items = [item for item in items if item.price <= max_price]
        if min_square_meters is not None:
            items = [item for item in items if item.square_meters >= min_square_meters]
        if max_square_meters is not None:
            items = [item for item in items if item.square_meters <= max_square_meters]
        total = len(items)
        items.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        start = (page - 1) * page_size
        return items[start : start + page_size], total
