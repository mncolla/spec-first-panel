from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.entities.image import DepartmentImage
from app.domain.entities.inquiry import Inquiry
from app.domain.exceptions import DomainError

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 120
MAX_DESCRIPTION_LENGTH = 4000
MAX_IMAGES = 5
MAX_SEEDED_IMAGES = 8


class Currency(StrEnum):
    USD = "USD"
    ARS = "ARS"


@dataclass
class Department:
    id: UUID
    title: str
    price: Decimal
    currency: Currency
    square_meters: Decimal
    address: str
    available: bool
    created_at: datetime
    description: str | None = None
    lat: float | None = None
    lng: float | None = None
    images: tuple[DepartmentImage, ...] = field(default_factory=tuple)
    inquiries: tuple[Inquiry, ...] = field(default_factory=tuple)
    inquiry_count: int | None = None

    def __post_init__(self) -> None:
        self._validate()

    @classmethod
    def create(
        cls,
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
        images: list[DepartmentImage] | tuple[DepartmentImage, ...] | None = None,
        inquiries: list[Inquiry] | tuple[Inquiry, ...] | None = None,
    ) -> "Department":
        try:
            currency_vo = Currency(currency)
        except ValueError as exc:
            raise DomainError("Currency must be USD or ARS") from exc

        description_text = description.strip() if description else None
        if description_text == "":
            description_text = None

        return cls(
            id=uuid4(),
            title=title.strip(),
            description=description_text,
            price=Decimal(price),
            currency=currency_vo,
            square_meters=Decimal(square_meters),
            address=address.strip(),
            lat=lat,
            lng=lng,
            available=available,
            images=_normalize_images(images),
            inquiries=_normalize_inquiries(inquiries),
            created_at=datetime.now(timezone.utc),
        )

    def update(
        self,
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
        images: list[DepartmentImage] | tuple[DepartmentImage, ...] | None,
    ) -> None:
        try:
            self.currency = Currency(currency)
        except ValueError as exc:
            raise DomainError("Currency must be USD or ARS") from exc

        description_text = description.strip() if description else None
        self.title = title.strip()
        self.description = None if description_text == "" else description_text
        self.price = Decimal(price)
        self.square_meters = Decimal(square_meters)
        self.address = address.strip()
        self.lat = lat
        self.lng = lng
        self.available = available
        self.images = _normalize_images(images)
        self._validate()

    def replace_images(self, images: list[DepartmentImage] | tuple[DepartmentImage, ...]) -> None:
        self.images = _normalize_images(images)
        self._validate()

    def replace_inquiries(self, inquiries: list[Inquiry] | tuple[Inquiry, ...]) -> None:
        self.inquiries = _normalize_inquiries(inquiries)
        self.inquiry_count = None
        self._validate()

    def add_inquiry(self, inquiry: Inquiry) -> Inquiry:
        if not self.available:
            raise DomainError(
                "Inquiries can only be recorded on available departments"
            )
        self.inquiries = _normalize_inquiries((*self.inquiries, inquiry))
        self.inquiry_count = None
        return inquiry

    def _validate(self) -> None:
        if not MIN_TITLE_LENGTH <= len(self.title) <= MAX_TITLE_LENGTH:
            raise DomainError(
                f"Title must be between {MIN_TITLE_LENGTH} and {MAX_TITLE_LENGTH} characters"
            )
        if (
            self.description is not None
            and len(self.description) > MAX_DESCRIPTION_LENGTH
        ):
            raise DomainError(
                f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters"
            )
        if self.price <= 0:
            raise DomainError("Price must be greater than 0")
        if self.square_meters <= 0:
            raise DomainError("Square meters must be greater than 0")
        if not self.address:
            raise DomainError("Address is required")
        if len(self.images) > MAX_SEEDED_IMAGES:
            raise DomainError(
                f"No more than {MAX_SEEDED_IMAGES} images are allowed"
            )

    @property
    def principal_image_url(self) -> str | None:
        return self.images[0].url if self.images else None

    @property
    def total_inquiries(self) -> int:
        if self.inquiry_count is not None:
            return self.inquiry_count
        return len(self.inquiries)


def _normalize_images(
    images: list[DepartmentImage] | tuple[DepartmentImage, ...] | None,
) -> tuple[DepartmentImage, ...]:
    return tuple(
        DepartmentImage(
            id=image.id,
            url=image.url,
            position=index,
            storage_key=image.storage_key,
        )
        for index, image in enumerate(images or ())
    )


def _normalize_inquiries(
    inquiries: list[Inquiry] | tuple[Inquiry, ...] | None,
) -> tuple[Inquiry, ...]:
    return tuple(
        sorted(
            inquiries or (),
            key=lambda inquiry: (inquiry.created_at, inquiry.id),
            reverse=True,
        )
    )
