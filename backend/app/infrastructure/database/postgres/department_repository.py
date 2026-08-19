from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, noload, selectinload

from app.domain.entities.department import Department
from app.infrastructure.database.postgres.models import (
    DepartmentModel,
    ImageModel,
    InquiryModel,
    entity_to_model,
    model_to_entity,
)


class PostgresDepartmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, department: Department) -> Department:
        row = entity_to_model(department)
        self._session.add(row)
        self._session.flush()
        return department

    def get(self, department_id: UUID) -> Department | None:
        row = self._session.get(
            DepartmentModel,
            department_id,
            options=(
                selectinload(DepartmentModel.images),
                selectinload(DepartmentModel.inquiries),
            ),
        )
        if row is None:
            return None
        return model_to_entity(row)

    def update(self, department: Department) -> Department:
        row = self._session.get(
            DepartmentModel,
            department.id,
            options=(
                selectinload(DepartmentModel.images),
                selectinload(DepartmentModel.inquiries),
            ),
        )
        if row is None:
            row = entity_to_model(department)
            self._session.add(row)
        else:
            row.title = department.title
            row.description = department.description
            row.price = department.price
            row.currency = department.currency.value
            row.square_meters = department.square_meters
            row.address = department.address
            row.lat = department.lat
            row.lng = department.lng
            row.available = department.available
            row.images.clear()
            row.inquiries.clear()
            self._session.flush()
            for image in department.images:
                row.images.append(
                    ImageModel(
                        id=image.id,
                        department_id=department.id,
                        url=image.url,
                        position=image.position,
                        storage_key=image.storage_key,
                    )
                )
            for inquiry in department.inquiries:
                row.inquiries.append(
                    InquiryModel(
                        id=inquiry.id,
                        department_id=department.id,
                        name=inquiry.name,
                        email=inquiry.email,
                        message=inquiry.message,
                        created_at=inquiry.created_at,
                    )
                )
        self._session.flush()
        return model_to_entity(
            row,
            inquiries=department.inquiries,
            inquiry_count=department.inquiry_count,
        )

    def list(
        self,
        *,
        page: int,
        page_size: int,
        available: bool | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        min_square_meters: Decimal | None = None,
        max_square_meters: Decimal | None = None,
    ) -> tuple[list[Department], int]:
        inquiry_count = (
            select(func.count())
            .select_from(InquiryModel)
            .where(InquiryModel.department_id == DepartmentModel.id)
            .correlate(DepartmentModel)
            .scalar_subquery()
        )
        filtered = self._apply_filters(
            select(DepartmentModel),
            available=available,
            min_price=min_price,
            max_price=max_price,
            min_square_meters=min_square_meters,
            max_square_meters=max_square_meters,
        )
        total = self._session.scalar(
            select(func.count()).select_from(filtered.subquery())
        ) or 0
        stmt = (
            filtered.add_columns(inquiry_count)
            .options(
                selectinload(DepartmentModel.images),
                noload(DepartmentModel.inquiries),
            )
            .order_by(DepartmentModel.created_at.desc(), DepartmentModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self._session.execute(stmt).all()
        return [
            model_to_entity(row, inquiries=(), inquiry_count=count or 0)
            for row, count in rows
        ], total

    def _apply_filters(
        self,
        stmt: Select[tuple[DepartmentModel]],
        *,
        available: bool | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        min_square_meters: Decimal | None,
        max_square_meters: Decimal | None,
    ) -> Select[tuple[DepartmentModel]]:
        if available is not None:
            stmt = stmt.where(DepartmentModel.available.is_(available))
        if min_price is not None:
            stmt = stmt.where(DepartmentModel.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(DepartmentModel.price <= max_price)
        if min_square_meters is not None:
            stmt = stmt.where(DepartmentModel.square_meters >= min_square_meters)
        if max_square_meters is not None:
            stmt = stmt.where(DepartmentModel.square_meters <= max_square_meters)
        return stmt
