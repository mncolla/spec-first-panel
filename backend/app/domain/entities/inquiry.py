from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.domain.exceptions import DomainError

MAX_INQUIRY_NAME_LENGTH = 120
MAX_INQUIRY_MESSAGE_LENGTH = 4000
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Inquiry:
    name: str
    email: str
    message: str
    created_at: datetime
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise DomainError("Inquiry name is required")
        if len(self.name) > MAX_INQUIRY_NAME_LENGTH:
            raise DomainError(
                f"Inquiry name cannot exceed {MAX_INQUIRY_NAME_LENGTH} characters"
            )
        if not self.message.strip():
            raise DomainError("Inquiry message is required")
        if len(self.message) > MAX_INQUIRY_MESSAGE_LENGTH:
            raise DomainError(
                f"Inquiry message cannot exceed {MAX_INQUIRY_MESSAGE_LENGTH} characters"
            )
        if _EMAIL.match(self.email.strip()) is None:
            raise DomainError("Inquiry email is invalid")

    @classmethod
    def create(
        cls,
        *,
        name: str,
        email: str,
        message: str,
        created_at: datetime | None = None,
    ) -> Inquiry:
        return cls(
            name=name.strip(),
            email=email.strip(),
            message=message.strip(),
            created_at=created_at or datetime.now(timezone.utc),
        )
