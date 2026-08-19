from uuid import UUID

from app.domain.entities.operator_session import OperatorSession


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, OperatorSession] = {}

    def add(self, session: OperatorSession) -> OperatorSession:
        self._items[session.id] = session
        return session

    def get(self, session_id: UUID) -> OperatorSession | None:
        return self._items.get(session_id)

    def delete(self, session_id: UUID) -> None:
        self._items.pop(session_id, None)
