from decimal import Decimal

from app.application.image_input import ImageInput
from app.application.ports.object_storage import ObjectStorage, store_department_images
from app.domain.entities.department import Department
from app.domain.repositories.department_repository import DepartmentRepository


def create_department(
    repo: DepartmentRepository,
    storage: ObjectStorage,
    *,
    title: str,
    price: Decimal,
    currency: str,
    square_meters: Decimal,
    address: str,
    description: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    available: bool = True,
    images: list[ImageInput] | None = None,
) -> Department:
    department = Department.create(
        title=title,
        price=price,
        currency=currency,
        square_meters=square_meters,
        address=address,
        description=description,
        lat=lat,
        lng=lng,
        available=available,
        images=(),
    )
    department.replace_images(
        store_department_images(
            storage,
            department.id,
            images or [],
            previous=(),
        )
    )
    return repo.add(department)
