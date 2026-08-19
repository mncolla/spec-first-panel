from typing import Protocol
from uuid import UUID, uuid4

from app.application.image_input import ImageInput, extension_for
from app.domain.entities.department import MAX_IMAGES
from app.domain.entities.image import DepartmentImage
from app.domain.exceptions import DomainError


class ObjectStorage(Protocol):
    def ensure_bucket(self) -> None: ...

    def public_url(self, key: str) -> str: ...

    def put(self, key: str, body: bytes, content_type: str) -> str: ...

    def delete(self, key: str) -> None: ...


def store_department_images(
    storage: ObjectStorage,
    department_id: UUID,
    images: list[ImageInput],
    *,
    previous: tuple[DepartmentImage, ...],
) -> list[DepartmentImage]:
    if len(images) > MAX_IMAGES:
        raise DomainError(f"No more than {MAX_IMAGES} images are allowed")
    kept_keys: set[str] = set()
    stored: list[DepartmentImage] = []
    for index, payload in enumerate(images):
        if payload.is_upload:
            assert payload.content is not None
            assert payload.content_type is not None
            image_id = uuid4()
            key = f"{department_id}/{image_id}{extension_for(payload.content_type)}"
            url = storage.put(key, payload.content, payload.content_type)
            stored.append(
                DepartmentImage(
                    id=image_id,
                    url=url,
                    position=index,
                    storage_key=key,
                )
            )
            kept_keys.add(key)
            continue

        assert payload.url is not None
        existing = next(
            (image for image in previous if image.url == payload.url),
            None,
        )
        if existing is not None and existing.storage_key:
            kept_keys.add(existing.storage_key)
            stored.append(
                DepartmentImage(
                    id=existing.id,
                    url=existing.url,
                    position=index,
                    storage_key=existing.storage_key,
                )
            )
        else:
            stored.append(
                DepartmentImage(url=payload.url, position=index, storage_key=None)
            )

    for image in previous:
        if image.storage_key and image.storage_key not in kept_keys:
            storage.delete(image.storage_key)

    return stored
