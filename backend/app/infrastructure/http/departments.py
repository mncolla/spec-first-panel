from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.application.image_input import parse_image_write
from app.application.ports.object_storage import ObjectStorage
from app.application.use_cases.auth.get_current_operator import CurrentAuth
from app.application.use_cases.departments.create_department import create_department
from app.application.use_cases.departments.create_inquiry import create_inquiry
from app.application.use_cases.departments.get_department import get_department
from app.application.use_cases.departments.list_departments import list_departments
from app.application.use_cases.departments.update_department import update_department
from app.domain.entities.department import Department
from app.domain.entities.inquiry import Inquiry
from app.domain.repositories.department_repository import DepartmentRepository
from app.infrastructure.container import get_department_repository, get_object_storage
from app.infrastructure.http.deps import require_operator
from app.infrastructure.http.schemas import (
    DepartmentDetail,
    DepartmentListItem,
    DepartmentListResponse,
    DepartmentWrite,
    InquiryDetail,
    InquiryWrite,
)

router = APIRouter(prefix="/departamentos", tags=["departamentos"])


class BackgroundObjectStorage:
    """Schedules put/delete after the response so POST can return 202 quickly."""

    def __init__(self, inner: ObjectStorage, tasks: BackgroundTasks) -> None:
        self._inner = inner
        self._tasks = tasks

    def ensure_bucket(self) -> None:
        self._inner.ensure_bucket()

    def public_url(self, key: str) -> str:
        return self._inner.public_url(key)

    def put(self, key: str, body: bytes, content_type: str) -> str:
        url = self._inner.public_url(key)
        self._tasks.add_task(self._inner.put, key, body, content_type)
        return url

    def delete(self, key: str) -> None:
        self._tasks.add_task(self._inner.delete, key)


def to_detail(department: Department) -> DepartmentDetail:
    return DepartmentDetail(
        id=department.id,
        titulo=department.title,
        descripcion=department.description,
        precio=department.price,
        moneda=department.currency.value,
        metros_cuadrados=department.square_meters,
        direccion=department.address,
        lat=department.lat,
        lng=department.lng,
        disponible=department.available,
        imagenes=[image.url for image in department.images],
        consultas=[to_inquiry_detail(inquiry) for inquiry in department.inquiries],
        created_at=department.created_at,
    )


def to_inquiry_detail(inquiry: Inquiry) -> InquiryDetail:
    return InquiryDetail(
        nombre=inquiry.name,
        email=inquiry.email,
        mensaje=inquiry.message,
        fecha=inquiry.created_at,
    )


def to_list_item(department: Department) -> DepartmentListItem:
    return DepartmentListItem(
        id=department.id,
        titulo=department.title,
        precio=department.price,
        moneda=department.currency.value,
        metros_cuadrados=department.square_meters,
        direccion=department.address,
        disponible=department.available,
        imagen_principal=department.principal_image_url,
        total_imagenes=len(department.images),
        total_consultas=department.total_inquiries,
    )


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def create(
    body: DepartmentWrite,
    background_tasks: BackgroundTasks,
    repo: DepartmentRepository = Depends(get_department_repository),
    storage: ObjectStorage = Depends(get_object_storage),
    _: CurrentAuth = Depends(require_operator),
) -> DepartmentDetail:
    created = create_department(
        repo,
        BackgroundObjectStorage(storage, background_tasks),
        title=body.titulo,
        price=body.precio,
        currency=body.moneda,
        square_meters=body.metros_cuadrados,
        address=body.direccion,
        description=body.descripcion,
        lat=body.lat,
        lng=body.lng,
        available=body.disponible,
        images=[parse_image_write(item) for item in body.imagenes],
    )
    return to_detail(created)


@router.get("")
def list_items(
    pagina: Annotated[int, Query(ge=1)] = 1,
    cantidad: Annotated[int, Query(ge=1, le=100)] = 20,
    disponible: bool | None = None,
    precio_min: Decimal | None = None,
    precio_max: Decimal | None = None,
    metros_min: Decimal | None = None,
    metros_max: Decimal | None = None,
    repo: DepartmentRepository = Depends(get_department_repository),
    _: CurrentAuth = Depends(require_operator),
) -> DepartmentListResponse:
    page = list_departments(
        repo,
        page=pagina,
        page_size=cantidad,
        available=disponible,
        min_price=precio_min,
        max_price=precio_max,
        min_square_meters=metros_min,
        max_square_meters=metros_max,
    )
    return DepartmentListResponse(
        items=[to_list_item(item) for item in page.items],
        pagina=page.page,
        cantidad=page.page_size,
        total=page.total,
    )


@router.get("/{department_id}")
def detail(
    department_id: UUID,
    repo: DepartmentRepository = Depends(get_department_repository),
    _: CurrentAuth = Depends(require_operator),
) -> DepartmentDetail:
    return to_detail(get_department(repo, department_id))


@router.put("/{department_id}")
def update_item(
    department_id: UUID,
    body: DepartmentWrite,
    background_tasks: BackgroundTasks,
    repo: DepartmentRepository = Depends(get_department_repository),
    storage: ObjectStorage = Depends(get_object_storage),
    _: CurrentAuth = Depends(require_operator),
) -> DepartmentDetail:
    updated = update_department(
        repo,
        BackgroundObjectStorage(storage, background_tasks),
        department_id,
        title=body.titulo,
        price=body.precio,
        currency=body.moneda,
        square_meters=body.metros_cuadrados,
        address=body.direccion,
        description=body.descripcion,
        lat=body.lat,
        lng=body.lng,
        available=body.disponible,
        images=[parse_image_write(item) for item in body.imagenes],
    )
    return to_detail(updated)


@router.post("/{department_id}/consultas", status_code=status.HTTP_201_CREATED)
def create_inquiry_item(
    department_id: UUID,
    body: InquiryWrite,
    repo: DepartmentRepository = Depends(get_department_repository),
    _: CurrentAuth = Depends(require_operator),
) -> InquiryDetail:
    inquiry = create_inquiry(
        repo,
        department_id,
        name=body.nombre,
        email=body.email,
        message=body.mensaje,
    )
    return to_inquiry_detail(inquiry)
