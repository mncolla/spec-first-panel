from decimal import Decimal
from typing import Protocol
from uuid import UUID

from app.domain.entities.department import Department


class DepartmentRepository(Protocol):
    def add(self, department: Department) -> Department: ...

    def get(self, department_id: UUID) -> Department | None: ...

    def update(self, department: Department) -> Department: ...

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
    ) -> tuple[list[Department], int]: ...
