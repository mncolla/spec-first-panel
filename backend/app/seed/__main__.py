"""CLI: `python -m app.seed` / `python -m app.seed --force`."""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import delete, func, select

from app.infrastructure.database.postgres.db import get_session_factory
from app.infrastructure.database.postgres.department_repository import (
    PostgresDepartmentRepository,
)
from app.infrastructure.database.postgres.models import DepartmentModel
from app.infrastructure.storage.s3.storage import get_s3_storage, try_ensure_bucket
from app.seed.catalog import DEFAULT_SEED_COUNT, plan_seed, seed_departments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the Lebane catalog")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing departments and seed again",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_SEED_COUNT,
        help=f"Departments to insert (default {DEFAULT_SEED_COUNT})",
    )
    args = parser.parse_args(argv)
    if args.count < 1:
        print("count must be >= 1", file=sys.stderr)
        return 2

    try_ensure_bucket()
    factory = get_session_factory()
    session = factory()
    try:
        existing = session.scalar(select(func.count()).select_from(DepartmentModel)) or 0
        action = plan_seed(existing, force=args.force)
        if action == "skip":
            print(f"Already seeded ({existing} departments). Pass --force to replace.")
            return 0
        if action == "refuse":
            print(
                f"There are already {existing} departments. "
                "Pass --force to delete them and seed from scratch.",
                file=sys.stderr,
            )
            return 2
        if action == "replace" and existing:
            session.execute(delete(DepartmentModel))
            session.flush()
            print(f"Removed {existing} existing departments.")

        stats = seed_departments(
            PostgresDepartmentRepository(session),
            get_s3_storage(),
            count=args.count,
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "Seeded {departments} departments "
        "({available} available, {usd} USD, {uploaded} images in MinIO, "
        "{broken} broken URLs, {inquiries} inquiries).".format(
            departments=stats.departments,
            available=stats.available,
            usd=stats.usd,
            uploaded=stats.images_uploaded,
            broken=stats.broken_image_urls,
            inquiries=stats.inquiries,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
