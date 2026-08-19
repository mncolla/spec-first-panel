from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.operator import Operator, OperatorRole
from app.infrastructure.database.postgres.models import (
    OperatorModel,
    operator_to_entity,
    operator_to_model,
)


class PostgresOperatorRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, operator: Operator) -> Operator:
        row = operator_to_model(operator)
        self._session.add(row)
        self._session.flush()
        return operator

    def get(self, operator_id: UUID) -> Operator | None:
        row = self._session.get(OperatorModel, operator_id)
        if row is None:
            return None
        return operator_to_entity(row)

    def get_by_email(self, email: str) -> Operator | None:
        stmt = select(OperatorModel).where(OperatorModel.email == email.strip().lower())
        row = self._session.scalar(stmt)
        if row is None:
            return None
        return operator_to_entity(row)

    def get_by_role(self, role: OperatorRole) -> Operator | None:
        stmt = select(OperatorModel).where(OperatorModel.role == role.value)
        row = self._session.scalar(stmt)
        if row is None:
            return None
        return operator_to_entity(row)
