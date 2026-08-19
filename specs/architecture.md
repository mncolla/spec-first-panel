# Architecture

Small monolith. Hexagonal / layered DDD backend (English code); feature-oriented frontend. The **HTTP contract** from the brief stays in Spanish (`/departamentos`, `titulo`, `consultas`, …): DTOs in `infrastructure/http/` are the anti-corruption layer.

## Stack

| Layer | Choice |
|---|---|
| API | FastAPI 0.14x, Python 3.12, Pydantic v2 |
| Persistence | SQLAlchemy 2 (query builder, no SQL strings) + PostgreSQL |
| Migrations | Alembic |
| Storage | MinIO (S3-compatible) via boto3 |
| Front | React 19, Vite, TypeScript, Tailwind 4 |
| Server state | TanStack Query |
| Routing | wouter |
| BE tests | pytest + httpx in `backend/tests/` |
| FE tests | Vitest + Testing Library (the brief says Jest; Vitest fits Vite) |
| Tooling | ruff (BE), oxlint (FE) |
| Local runtime | Docker Compose: API + Postgres + MinIO |

## Backend — hexagonal / layered DDD

Pydantic lives in the HTTP adapter (`infrastructure/http/`), not in domain or use cases. The department repository is a domain contract. MinIO/S3 is not: the `ObjectStorage` port (and how it applies to department photos) lives in `application/ports/object_storage.py`. Infrastructure implements the port. `container.py` is the composition root.

```
backend/
├── app/
│   ├── main.py
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── department.py
│   │   │   ├── image.py
│   │   │   └── inquiry.py
│   │   ├── repositories/
│   │   │   └── department_repository.py   # Protocol
│   │   └── exceptions.py
│   ├── application/
│   │   ├── exceptions.py
│   │   ├── ports/
│   │   │   └── object_storage.py          # Protocol + store images
│   │   └── use_cases/
│   │       ├── create_department.py
│   │       ├── list_departments.py
│   │       ├── get_department.py
│   │       ├── update_department.py
│   │       └── create_inquiry.py
│   ├── infrastructure/
│   │   ├── container.py                   # composition root
│   │   ├── config/settings.py
│   │   ├── database/
│   │   │   ├── postgres/
│   │   │   │   ├── db.py
│   │   │   │   ├── models.py
│   │   │   │   └── department_repository.py
│   │   │   └── memory/
│   │   │       └── department_repository.py
│   │   ├── storage/
│   │   │   ├── s3/storage.py
│   │   │   └── memory/storage.py
│   │   └── http/                          # driving adapter
│   │       ├── departments.py
│   │       └── schemas.py                 # Pydantic; Spanish JSON (brief)
│   └── seed/                              # local tooling, not a use case
│       ├── catalog.py
│       └── __main__.py                    # python -m app.seed
└── tests/
    ├── domain/
    ├── application/
    ├── infrastructure/
    ├── api/
    └── seed/
```

Rules:

- `domain/` does not import FastAPI, SQLAlchemy, Pydantic, or S3. Entities, invariants, repository contracts.
- `application/` orchestrates use cases against domain repositories. Object storage port: `application/ports/object_storage.py`. Tests use `memory/` adapters.
- `app/seed/` is local tooling (`python -m app.seed`), not a panel use case.
- `infrastructure/` implements ports, grouped by technology. Integration tests hit Postgres (`DATABASE_URL`). The HTTP driving adapter lives in `infrastructure/http/`.
- `infrastructure/http/` is HTTP only: parse, status codes, Spanish DTO ↔ English entity. It does not build SQLAlchemy sessions by hand: it asks `container` for dependencies.
- Validation: Pydantic covers types/required (`422`). Domain is the source of truth; the handler maps `DomainError` to `422`. `404` = not found.
- List filters: composable SQLAlchemy expressions. No `text()` / concatenated SQL.
- `POST /departamentos` returns `202` with the resource in the body. Row persist is synchronous; image upload may run in `BackgroundTasks`.
- `POST /departamentos/{id}/consultas` returns `201` with the created inquiry. Recording an inquiry is a command on the `Department` aggregate (`add_inquiry`), not a separate bounded context.
- Code and files in English. No `consultas/` or `imagenes/` packages: `domain/entities/inquiry.py` / `image.py`. Frontend inquiry UI stays in `features/departments/`.
- DB tables `departments`, `images`, `inquiries`. HTTP: `imagenes`, `consultas`.

## Frontend — feature-oriented

```
frontend/src/
├── app/                         # shell, providers, router
├── lib/                         # api client
└── features/
    ├── departments/
    │   ├── components/
    │   ├── hooks/
    │   ├── services/
    │   └── types.ts
    └── address/
        ├── components/
        ├── hooks/
        └── services/
```

Rules:

- One feature = UI + hooks + services for that domain. Do not leak department logic into a global `src/components/`.
- Shared `components/` only if used by ≥ 2 features.
- No `actions/` folder: mutations live in `hooks/` (React Query) and `services/` (fetch).
- `contexts/` only for truly global UI state. Prefer Query + props.
- Broken image: placeholder in the thumbnail/gallery, never a crash.

Routes:

| Path | Screen |
|---|---|
| `/` | list |
| `/departamentos/nuevo` | create |
| `/departamentos/:id` | detail + edit |

## Images

Server-side upload to MinIO. The panel sends data URLs (or existing `http(s)` URLs on PUT). Public URLs (via `S3_PUBLIC_ENDPOINT`) for the UI. The UI assumes a URL may fail.

## Address

Nominatim / OpenStreetMap in the browser (no paid API key). Persist `direccion` (text), `lat`, and `lng`. The backend does not call the map provider.

## Inquiries

The operator records them on the detail screen. Nested `POST /departamentos/{id}/consultas`; only when `disponible` is true. Delisted → `DomainError` (`422`), not `409`. Seed (feature 06) still generates history; PUT on the department does not create or delete inquiries.

## Errors

Backend: consistent handlers (`422` validation, `404` not found, `500` unexpected). Front: `pending` / `error` / `empty` on every screen that hits the API.
