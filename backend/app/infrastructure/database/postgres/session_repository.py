from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.entities.operator_session import OperatorSession
from app.infrastructure.database.postgres.models import (
    OperatorSessionModel,
    session_to_entity,
    session_to_model,
)


class PostgresSessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, session: OperatorSession) -> OperatorSession:
        row = session_to_model(session)
        self._session.add(row)
        self._session.flush()
        return session

    def get(self, session_id: UUID) -> OperatorSession | None:
        row = self._session.get(OperatorSessionModel, session_id)
        if row is None:
            return None
        return session_to_entity(row)

    def delete(self, session_id: UUID) -> None:
        row = self._session.get(OperatorSessionModel, session_id)
        if row is not None:
            self._session.delete(row)
            self._session.flush()
