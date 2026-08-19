from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.domain.entities.department import (
    MAX_DESCRIPTION_LENGTH,
    MAX_IMAGES,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
)
from app.domain.entities.inquiry import MAX_INQUIRY_MESSAGE_LENGTH, MAX_INQUIRY_NAME_LENGTH


class DepartmentWrite(BaseModel):
    """HTTP write DTO. Field names match the PDF contract (Spanish)."""

    titulo: str = Field(min_length=MIN_TITLE_LENGTH, max_length=MAX_TITLE_LENGTH)
    descripcion: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)
    precio: Decimal = Field(gt=0)
    moneda: str = Field(pattern="^(USD|ARS)$")
    metros_cuadrados: Decimal = Field(gt=0)
    direccion: str = Field(min_length=1)
    lat: float | None = None
    lng: float | None = None
    disponible: bool = True
    imagenes: list[str] = Field(default_factory=list, max_length=MAX_IMAGES)

    @field_validator("titulo", "direccion")
    @classmethod
    def strip_required(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("cannot be blank")
        return stripped

    @field_validator("imagenes")
    @classmethod
    def strip_images(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class DepartmentListItem(BaseModel):
    id: UUID
    titulo: str
    precio: Decimal
    moneda: str
    metros_cuadrados: Decimal
    direccion: str
    disponible: bool
    imagen_principal: str | None = None
    total_imagenes: int = 0
    total_consultas: int = 0

    @field_serializer("precio", "metros_cuadrados")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)


class DepartmentListResponse(BaseModel):
    items: list[DepartmentListItem]
    pagina: int
    cantidad: int
    total: int


class InquiryWrite(BaseModel):
    nombre: str = Field(min_length=1, max_length=MAX_INQUIRY_NAME_LENGTH)
    email: str = Field(min_length=1)
    mensaje: str = Field(min_length=1, max_length=MAX_INQUIRY_MESSAGE_LENGTH)

    @field_validator("nombre", "email", "mensaje")
    @classmethod
    def strip_required(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("cannot be blank")
        return stripped


class InquiryDetail(BaseModel):
    nombre: str
    email: str
    mensaje: str
    fecha: datetime

    @field_serializer("fecha")
    def serialize_fecha(self, value: datetime) -> str:
        aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return aware.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class SessionWrite(BaseModel):
    email: str = Field(min_length=1)
    clave: str = Field(min_length=8)

    @field_validator("email", "clave")
    @classmethod
    def strip_session(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("cannot be blank")
        return stripped


class SessionPublic(BaseModel):
    email: str
    rol: str


class SessionCreated(SessionPublic):
    token: str


class OperatorWrite(BaseModel):
    email: str = Field(min_length=1)
    clave: str = Field(min_length=8)
    rol: str = Field(pattern="^agente$")

    @field_validator("email", "clave")
    @classmethod
    def strip_operator(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("cannot be blank")
        return stripped


class OperatorDetail(BaseModel):
    email: str
    rol: str


class DepartmentDetail(BaseModel):
    id: UUID
    titulo: str
    descripcion: str | None
    precio: Decimal
    moneda: str
    metros_cuadrados: Decimal
    direccion: str
    lat: float | None
    lng: float | None
    disponible: bool
    imagenes: list[str]
    consultas: list[InquiryDetail]
    created_at: datetime

    @field_serializer("precio", "metros_cuadrados")
    def serialize_decimal(self, value: Decimal) -> float:
        return float(value)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return aware.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
