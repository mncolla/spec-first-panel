from random import Random

from app.infrastructure.database.memory.department_repository import InMemoryDepartmentRepository
from app.infrastructure.storage.memory.storage import InMemoryStorage
from app.seed.catalog import (
    BROKEN_IMAGE_URL,
    plan_seed,
    seed_departments,
)


def test_plan_seed_inserts_when_empty() -> None:
    assert plan_seed(0, force=False) == "insert"


def test_plan_seed_skips_when_already_full() -> None:
    assert plan_seed(500, force=False) == "skip"


def test_plan_seed_refuses_partial_catalog() -> None:
    assert plan_seed(12, force=False) == "refuse"


def test_plan_seed_force_replaces() -> None:
    assert plan_seed(12, force=True) == "replace"
    assert plan_seed(500, force=True) == "replace"


def test_seed_catalog_is_heterogeneous() -> None:
    repo = InMemoryDepartmentRepository()
    storage = InMemoryStorage()
    stats = seed_departments(repo, storage, count=40, rng=Random(42))

    items, total = repo.list(page=1, page_size=40)
    assert total == 40
    assert stats.departments == 40
    assert 0 < stats.available < 40
    assert 0 < stats.usd < 40
    assert stats.images_uploaded == len(storage.objects)
    assert stats.images_uploaded > 0
    assert stats.broken_image_urls > 0
    assert stats.inquiries > 0

    image_counts = [len(item.images) for item in items]
    inquiry_counts = [item.total_inquiries for item in items]
    assert min(image_counts) == 0
    assert max(image_counts) > 5
    assert min(inquiry_counts) == 0
    assert max(inquiry_counts) > 0
    assert any(
        any(image.url == BROKEN_IMAGE_URL for image in item.images) for item in items
    )
    currencies = {item.currency.value for item in items}
    assert currencies == {"USD", "ARS"}
    availabilities = {item.available for item in items}
    assert availabilities == {True, False}
