from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.exceptions import DomainError

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class OperatorRole(StrEnum):
    ADMIN = "admin"
    AGENT = "agent"

    def to_http(self) -> str:
        if self is OperatorRole.ADMIN:
            return "admin"
        return "agente"

    @classmethod
    def from_http(cls, value: str) -> OperatorRole:
        if value == "admin":
            return cls.ADMIN
        if value == "agente":
            return cls.AGENT
        raise DomainError("Role must be admin or agente")


@dataclass(frozen=True)
class Operator:
    email: str
    password_hash: str
    role: OperatorRole
    created_at: datetime
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if _EMAIL.match(self.email.strip()) is None:
            raise DomainError("Operator email is invalid")
        if not self.password_hash:
            raise DomainError("Operator password hash is required")

    @classmethod
    def create(
        cls,
        *,
        email: str,
        password_hash: str,
        role: OperatorRole,
        created_at: datetime | None = None,
    ) -> Operator:
        return cls(
            email=email.strip().lower(),
            password_hash=password_hash,
            role=role,
            created_at=created_at or datetime.now(timezone.utc),
        )
