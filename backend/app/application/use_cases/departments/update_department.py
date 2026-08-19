from decimal import Decimal
from uuid import UUID

from app.application.exceptions import NotFoundError
from app.application.image_input import ImageInput
from app.application.ports.object_storage import ObjectStorage, store_department_images
from app.domain.entities.department import Department
from app.domain.repositories.department_repository import DepartmentRepository


def update_department(
    repo: DepartmentRepository,
    storage: ObjectStorage,
    department_id: UUID,
    *,
    title: str,
    price: Decimal,
    currency: str,
    square_meters: Decimal,
    address: str,
    description: str | None,
    lat: float | None,
    lng: float | None,
    available: bool,
    images: list[ImageInput] | None,
) -> Department:
    existing = repo.get(department_id)
    if existing is None:
        raise NotFoundError

    existing.update(
        title=title,
        price=price,
        currency=currency,
        square_meters=square_meters,
        address=address,
        description=description,
        lat=lat,
        lng=lng,
        available=available,
        images=store_department_images(
            storage,
            existing.id,
            images or [],
            previous=existing.images,
        ),
    )
    return repo.update(existing)
