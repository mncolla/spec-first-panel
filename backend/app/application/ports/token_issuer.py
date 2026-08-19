from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class TokenClaims:
    session_id: UUID
    operator_id: UUID
    role: str
    expires_at: datetime


class TokenIssuer(Protocol):
    def issue(self, claims: TokenClaims) -> str: ...

    def parse(self, token: str) -> TokenClaims | None: ...
