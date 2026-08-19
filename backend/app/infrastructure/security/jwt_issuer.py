from datetime import UTC, datetime
from uuid import UUID

import jwt

from app.application.ports.token_issuer import TokenClaims, TokenIssuer
from app.infrastructure.config.settings import get_settings


class JwtTokenIssuer:
    def __init__(self, secret: str) -> None:
        self._secret = secret

    def issue(self, claims: TokenClaims) -> str:
        payload = {
            "sub": str(claims.operator_id),
            "jti": str(claims.session_id),
            "rol": claims.role,
            "exp": int(claims.expires_at.timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    def parse(self, token: str) -> TokenClaims | None:
        try:
            payload = jwt.decode(token, self._secret, algorithms=["HS256"])
            expires = datetime.fromtimestamp(payload["exp"], tz=UTC)
            return TokenClaims(
                session_id=UUID(payload["jti"]),
                operator_id=UUID(payload["sub"]),
                role=str(payload["rol"]),
                expires_at=expires,
            )
        except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
            return None


def get_token_issuer() -> TokenIssuer:
    return JwtTokenIssuer(get_settings().session_secret)
