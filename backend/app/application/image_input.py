from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass

from app.domain.exceptions import DomainError

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
_DATA_URL = re.compile(
    r"^data:(image/(?:jpeg|jpg|png|webp|gif));base64,([A-Za-z0-9+/=\s]+)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ImageInput:
    url: str | None = None
    content: bytes | None = None
    content_type: str | None = None

    @property
    def is_upload(self) -> bool:
        return self.content is not None


def parse_image_write(value: str) -> ImageInput:
    stripped = value.strip()
    if stripped.startswith(("http://", "https://")):
        return ImageInput(url=stripped)

    match = _DATA_URL.match(stripped)
    if match is None:
        raise DomainError("Image must be an http(s) URL or an image data URL")

    content_type = match.group(1).lower()
    if content_type == "image/jpg":
        content_type = "image/jpeg"
    try:
        content = base64.b64decode(match.group(2), validate=True)
    except binascii.Error as exc:
        raise DomainError("Image data URL is not valid base64") from exc
    if not content:
        raise DomainError("Image payload is empty")
    if len(content) > MAX_IMAGE_BYTES:
        raise DomainError(f"Each image must be at most {MAX_IMAGE_BYTES} bytes")
    return ImageInput(content=content, content_type=content_type)


def extension_for(content_type: str) -> str:
    return ALLOWED_CONTENT_TYPES[content_type]
