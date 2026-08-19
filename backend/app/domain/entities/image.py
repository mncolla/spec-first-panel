from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.exceptions import DomainError


@dataclass(frozen=True)
class DepartmentImage:
    url: str
    position: int
    id: UUID = field(default_factory=uuid4)
    storage_key: str | None = None

    def __post_init__(self) -> None:
        if not self.url.strip():
            raise DomainError("Image URL is required")
        if self.position < 0:
            raise DomainError("Image position must be >= 0")
