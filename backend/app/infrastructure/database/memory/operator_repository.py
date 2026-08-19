from uuid import UUID

from app.domain.entities.operator import Operator, OperatorRole


class InMemoryOperatorRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Operator] = {}

    def add(self, operator: Operator) -> Operator:
        self._items[operator.id] = operator
        return operator

    def get(self, operator_id: UUID) -> Operator | None:
        return self._items.get(operator_id)

    def get_by_email(self, email: str) -> Operator | None:
        needle = email.strip().lower()
        return next((item for item in self._items.values() if item.email == needle), None)

    def get_by_role(self, role: OperatorRole) -> Operator | None:
        return next((item for item in self._items.values() if item.role is role), None)
