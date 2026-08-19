from uuid import UUID

from app.domain.repositories.session_repository import SessionRepository


def logout(sessions: SessionRepository, session_id: UUID) -> None:
    sessions.delete(session_id)
