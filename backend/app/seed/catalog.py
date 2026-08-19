from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from random import Random
from uuid import uuid4

from app.application.ports.object_storage import ObjectStorage
from app.domain.entities.department import Department
from app.domain.entities.image import DepartmentImage
from app.domain.entities.inquiry import Inquiry
from app.domain.repositories.department_repository import DepartmentRepository

PLACEHOLDER_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
BROKEN_IMAGE_URL = "https://invalid.lebane.local/missing.jpg"
DEFAULT_SEED_COUNT = 500

_ADDRESSES: tuple[tuple[str, float | None, float | None], ...] = (
    ("Av. Santa Fe 3500, Palermo, CABA", -34.588, -58.411),
    ("Av. Cabildo 2200, Belgrano, CABA", -34.562, -58.456),
    ("Defensa 800, San Telmo, CABA", -34.621, -58.373),
    ("Av. Corrientes 1200, San Nicolás, CABA", -34.604, -58.384),
    ("Av. Rivadavia 5400, Caballito, CABA", -34.618, -58.441),
    ("Thames 1600, Villa Crespo, CABA", -34.598, -58.441),
    ("Av. del Libertador 7900, Núñez, CABA", -34.548, -58.454),
    ("Av. Independencia 2500, San Cristóbal, CABA", -34.622, -58.402),
    ("Av. Juan B. Justo 4700, Palermo Hollywood, CABA", -34.585, -58.435),
    ("Av. Las Heras 2100, Recoleta, CABA", -34.588, -58.397),
    ("Av. Directorio 1800, Parque Chacabuco, CABA", -34.635, -58.441),
    ("Av. San Juan 2700, Boedo, CABA", -34.626, -58.416),
    ("Av. Córdoba 4300, Palermo, CABA", -34.597, -58.421),
    ("Av. Callao 900, Recoleta, CABA", -34.597, -58.392),
    ("Av. Gaona 2800, Flores, CABA", -34.628, -58.464),
    ("Av. Maipú 2500, Vicente López, Buenos Aires", -34.526, -58.480),
    ("Av. Rivadavia 14100, Ramos Mejía, Buenos Aires", -34.642, -58.566),
    ("Av. Mitre 750, Avellaneda, Buenos Aires", -34.663, -58.365),
    ("Calle 12 800, La Plata, Buenos Aires", None, None),
    ("Av. Centenario 1500, San Isidro, Buenos Aires", -34.474, -58.508),
)

_TITLES = (
    "{n} ambientes en {barrio}",
    "Departamento en {barrio}",
    "PH luminoso en {barrio}",
    "Monoambiente en {barrio}",
    "Piso alto en {barrio}",
)
_BARRIOS = (
    "Palermo",
    "Belgrano",
    "San Telmo",
    "Caballito",
    "Villa Crespo",
    "Núñez",
    "Recoleta",
    "Boedo",
    "Flores",
    "Vicente López",
    "Ramos Mejía",
    "Avellaneda",
    "San Isidro",
)
_FIRST_NAMES = ("Ana", "Beto", "Cora", "Diego", "Elena", "Facundo", "Gina", "Hugo")
_LAST_NAMES = ("Pérez", "López", "García", "Fernández", "Romero", "Silva")
_MESSAGES = (
    "¿Sigue disponible?",
    "¿Se puede visitar el fin de semana?",
    "¿Aceptan mascotas?",
    "¿El precio es negociable?",
    "Me interesa, ¿cuál es el estado del edificio?",
    "¿Incluye expensas?",
    "Quiero agendar una visita.",
)


@dataclass(frozen=True)
class SeedStats:
    departments: int
    images_uploaded: int
    broken_image_urls: int
    inquiries: int
    available: int
    usd: int


def plan_seed(existing_count: int, *, force: bool) -> str:
    if force:
        return "replace"
    if existing_count >= DEFAULT_SEED_COUNT:
        return "skip"
    if existing_count > 0:
        return "refuse"
    return "insert"


def seed_departments(
    repo: DepartmentRepository,
    storage: ObjectStorage,
    *,
    count: int = DEFAULT_SEED_COUNT,
    rng: Random | None = None,
) -> SeedStats:
    rng = rng or Random(42)
    now = datetime.now(timezone.utc)
    uploaded = 0
    broken = 0
    inquiries = 0
    available = 0
    usd = 0

    for index in range(count):
        department = _build_department(rng, now, index)
        images, uploaded_delta, broken_delta = _build_images(
            rng, storage, department.id
        )
        department.replace_images(images)
        built_inquiries = _build_inquiries(rng, now)
        department.replace_inquiries(built_inquiries)
        repo.add(department)
        uploaded += uploaded_delta
        broken += broken_delta
        inquiries += len(built_inquiries)
        if department.available:
            available += 1
        if department.currency.value == "USD":
            usd += 1

    return SeedStats(
        departments=count,
        images_uploaded=uploaded,
        broken_image_urls=broken,
        inquiries=inquiries,
        available=available,
        usd=usd,
    )


def _build_department(rng: Random, now: datetime, index: int) -> Department:
    address, lat, lng = rng.choice(_ADDRESSES)
    barrio = rng.choice(_BARRIOS)
    rooms = rng.choice((1, 1, 2, 2, 2, 3, 3, 4))
    title = rng.choice(_TITLES).format(n=rooms, barrio=barrio)
    currency = "USD" if rng.random() < 0.55 else "ARS"
    if currency == "USD":
        price = Decimal(rng.randint(75, 420) * 1000)
    else:
        price = Decimal(rng.randint(40, 380) * 1_000_000)
    meters = Decimal(rng.randint(28, 160))
    use_coords = lat is not None and rng.random() > 0.08
    department = Department.create(
        title=title,
        price=price,
        currency=currency,
        square_meters=meters,
        address=address,
        description=_description(rng, title, meters),
        lat=lat if use_coords else None,
        lng=lng if use_coords else None,
        available=rng.random() > 0.22,
    )
    department.created_at = now - timedelta(days=rng.randint(0, 200), hours=index % 24)
    return department


def _description(rng: Random, title: str, meters: Decimal) -> str | None:
    if rng.random() < 0.15:
        return None
    return f"{title}. {meters} m², luminoso, a pocas cuadras de transporte."


def _build_images(
    rng: Random,
    storage: ObjectStorage,
    department_id,
) -> tuple[list[DepartmentImage], int, int]:
    count = rng.choices(
        population=list(range(9)),
        weights=[18, 22, 18, 14, 10, 8, 5, 3, 2],
        k=1,
    )[0]
    images: list[DepartmentImage] = []
    uploaded = 0
    broken = 0
    include_broken = count > 0 and rng.random() < 0.12
    for position in range(count):
        is_last_broken = include_broken and position == count - 1
        if is_last_broken:
            images.append(
                DepartmentImage(url=BROKEN_IMAGE_URL, position=position)
            )
            broken += 1
            continue
        image_id = uuid4()
        key = f"{department_id}/{image_id}.png"
        url = storage.put(key, PLACEHOLDER_PNG, "image/png")
        images.append(
            DepartmentImage(
                id=image_id,
                url=url,
                position=position,
                storage_key=key,
            )
        )
        uploaded += 1
    return images, uploaded, broken


def _build_inquiries(rng: Random, now: datetime) -> list[Inquiry]:
    count = rng.choices(
        population=[0, 1, 2, 3, 5, 8, 12, 20, 32, 40],
        weights=[28, 18, 14, 12, 10, 7, 5, 3, 2, 1],
        k=1,
    )[0]
    inquiries: list[Inquiry] = []
    for offset in range(count):
        first = rng.choice(_FIRST_NAMES)
        last = rng.choice(_LAST_NAMES)
        inquiries.append(
            Inquiry.create(
                name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}{offset}@mail.com",
                message=rng.choice(_MESSAGES),
                created_at=now - timedelta(days=rng.randint(0, 120), hours=offset),
            )
        )
    return inquiries
