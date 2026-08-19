from typing import Protocol
from uuid import UUID

from app.domain.entities.operator_session import OperatorSession


class SessionRepository(Protocol):
    def add(self, session: OperatorSession) -> OperatorSession: ...

    def get(self, session_id: UUID) -> OperatorSession | None: ...

    def delete(self, session_id: UUID) -> None: ...
