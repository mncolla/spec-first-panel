from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.department import Currency, Department
from app.domain.entities.image import DepartmentImage
from app.domain.entities.inquiry import Inquiry
from app.domain.entities.operator import Operator, OperatorRole
from app.domain.entities.operator_session import OperatorSession
from app.infrastructure.database.postgres.db import Base


class DepartmentModel(Base):
    __tablename__ = "departments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    square_meters: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    images: Mapped[list["ImageModel"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
        order_by="ImageModel.position",
    )
    inquiries: Mapped[list["InquiryModel"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
        order_by="InquiryModel.created_at.desc()",
        lazy="noload",
    )


class ImageModel(Base):
    __tablename__ = "images"
    __table_args__ = (UniqueConstraint("department_id", "position"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    department_id: Mapped[UUID] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)

    department: Mapped[DepartmentModel] = relationship(back_populates="images")


class InquiryModel(Base):
    __tablename__ = "inquiries"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    department_id: Mapped[UUID] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    department: Mapped[DepartmentModel] = relationship(back_populates="inquiries")


class OperatorModel(Base):
    __tablename__ = "operators"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sessions: Mapped[list["OperatorSessionModel"]] = relationship(
        back_populates="operator",
        cascade="all, delete-orphan",
    )


class OperatorSessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    operator_id: Mapped[UUID] = mapped_column(
        ForeignKey("operators.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    operator: Mapped[OperatorModel] = relationship(back_populates="sessions")


def model_to_entity(
    row: DepartmentModel,
    *,
    inquiries: tuple[Inquiry, ...] | None = None,
    inquiry_count: int | None = None,
) -> Department:
    created = row.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    images = tuple(
        DepartmentImage(
            id=image.id,
            url=image.url,
            position=image.position,
            storage_key=image.storage_key,
        )
        for image in sorted(row.images, key=lambda item: item.position)
    )
    if inquiries is None:
        inquiries = tuple(
            _inquiry_to_entity(item)
            for item in sorted(
                row.inquiries,
                key=lambda item: (item.created_at, item.id),
                reverse=True,
            )
        )
    return Department(
        id=row.id,
        title=row.title,
        description=row.description,
        price=row.price,
        currency=Currency(row.currency),
        square_meters=row.square_meters,
        address=row.address,
        lat=row.lat,
        lng=row.lng,
        available=row.available,
        images=images,
        inquiries=inquiries,
        inquiry_count=inquiry_count,
        created_at=created,
    )


def entity_to_model(department: Department) -> DepartmentModel:
    row = DepartmentModel(
        id=department.id,
        title=department.title,
        description=department.description,
        price=department.price,
        currency=department.currency.value,
        square_meters=department.square_meters,
        address=department.address,
        lat=department.lat,
        lng=department.lng,
        available=department.available,
        created_at=department.created_at,
    )
    row.images = [_image_to_model(department.id, image) for image in department.images]
    row.inquiries = [
        _inquiry_to_model(department.id, inquiry) for inquiry in department.inquiries
    ]
    return row


def _image_to_model(department_id: UUID, image: DepartmentImage) -> ImageModel:
    return ImageModel(
        id=image.id,
        department_id=department_id,
        url=image.url,
        position=image.position,
        storage_key=image.storage_key,
    )


def _inquiry_to_model(department_id: UUID, inquiry: Inquiry) -> InquiryModel:
    return InquiryModel(
        id=inquiry.id,
        department_id=department_id,
        name=inquiry.name,
        email=inquiry.email,
        message=inquiry.message,
        created_at=inquiry.created_at,
    )


def _inquiry_to_entity(row: InquiryModel) -> Inquiry:
    created = row.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    return Inquiry(
        id=row.id,
        name=row.name,
        email=row.email,
        message=row.message,
        created_at=created,
    )


def operator_to_entity(row: OperatorModel) -> Operator:
    created = row.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    return Operator(
        id=row.id,
        email=row.email,
        password_hash=row.password_hash,
        role=OperatorRole(row.role),
        created_at=created,
    )


def operator_to_model(operator: Operator) -> OperatorModel:
    return OperatorModel(
        id=operator.id,
        email=operator.email,
        password_hash=operator.password_hash,
        role=operator.role.value,
        created_at=operator.created_at,
    )


def session_to_entity(row: OperatorSessionModel) -> OperatorSession:
    expires = row.expires_at
    created = row.created_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    return OperatorSession(
        id=row.id,
        operator_id=row.operator_id,
        expires_at=expires,
        created_at=created,
    )


def session_to_model(session: OperatorSession) -> OperatorSessionModel:
    return OperatorSessionModel(
        id=session.id,
        operator_id=session.operator_id,
        expires_at=session.expires_at,
        created_at=session.created_at,
    )
