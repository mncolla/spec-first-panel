# Feature: Departments API

status: done

## Goal

Departments API on layered DDD: entity in `domain/`, use cases in `application/`, repository in `infrastructure/`. Contract and validation from `product.md`.

## Scope

**In**

- `Department` entity (domain invariants)
- `DepartmentRepository` protocol in `domain/repositories/` + `PostgresDepartmentRepository`
- Use cases: create, list, get, update
- Type-safe filters: `disponible`, `precio_min`, `precio_max`, `metros_min`, `metros_max` (AND, inclusive ranges)
- Pagination `pagina` + `cantidad`
- Request/response DTOs in `schemas.py` (not the entity)
- `POST` → `202` + detail in the body
- List item placeholders until 03/04: `imagen_principal: null`, `total_imagenes: 0`, `total_consultas: 0`
- Detail placeholders until 03/04: `imagenes: []`, `consultas: []`
- `PUT` full replacement → `200` detail or `404`
- Alembic: `departments` table with nullable `lat` / `lng`
- Tests: domain and create (in-memory repo); list filters against Postgres

**Out**

- S3 upload / persisted images (03)
- Persisted inquiries (04)
- Nominatim autocomplete (05); here we only store text + coords if present
- 500-row seed (06)
- CORS / panel client (07)

## JSON contract

`id`: server-generated UUID. `created_at`: ISO-8601 UTC, read-only.

### POST /departamentos

Request:

```json
{
  "titulo": "3 ambientes en Palermo",
  "descripcion": "Luminoso, a 2 cuadras del subte.",
  "precio": 180000,
  "moneda": "USD",
  "metros_cuadrados": 72.5,
  "direccion": "Av. Santa Fe 3500, Palermo, CABA",
  "lat": -34.588,
  "lng": -58.411,
  "disponible": true,
  "imagenes": []
}
```

| Field | Required | Notes |
|---|---|---|
| `titulo` | yes | 3–120 |
| `descripcion` | no | max 4000; omit or `null` → `null` |
| `precio` | yes | number `> 0` |
| `moneda` | yes | `USD` or `ARS` |
| `metros_cuadrados` | yes | number `> 0` |
| `direccion` | yes | non-empty text |
| `lat` / `lng` | no | floats; persisted when sent |
| `disponible` | no | default `true` |
| `imagenes` | no | default `[]`. Each item is a data URL (`data:image/jpeg\|png\|webp\|gif;base64,...`) or an `http(s)` URL. More than 5 → `422`. Format detail in [feature 03](03-images.md). |

Response `202` — same shape as detail.

Errors: Pydantic or domain validation → `422`.

### GET /departamentos

Query: `pagina` (int ≥ 1, default 1), `cantidad` (int 1–100, default 20), `disponible` (optional bool), `precio_min`, `precio_max`, `metros_min`, `metros_max` (optional numbers). Price filter does **not** split by currency.

Response `200`:

```json
{
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "titulo": "3 ambientes en Palermo",
      "precio": 180000,
      "moneda": "USD",
      "metros_cuadrados": 72.5,
      "direccion": "Av. Santa Fe 3500, Palermo, CABA",
      "disponible": true,
      "imagen_principal": null,
      "total_imagenes": 0,
      "total_consultas": 0
    }
  ],
  "pagina": 1,
  "cantidad": 20,
  "total": 1
}
```

Order: `created_at` desc, `id` desc. Out-of-range `pagina` → `items: []` and the real `total` (not 404).

### GET /departamentos/{id}

Response `200` detail:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "titulo": "3 ambientes en Palermo",
  "descripcion": "Luminoso, a 2 cuadras del subte.",
  "precio": 180000,
  "moneda": "USD",
  "metros_cuadrados": 72.5,
  "direccion": "Av. Santa Fe 3500, Palermo, CABA",
  "lat": -34.588,
  "lng": -58.411,
  "disponible": true,
  "imagenes": [],
  "consultas": [],
  "created_at": "2026-08-18T19:00:00Z"
}
```

Missing → `404` `{ "detail": "Department not found" }`.

Detail `consultas`: `{ nombre, email, mensaje, fecha }` ordered by date desc. The list only exposes `total_consultas` (feature 04).

### PUT /departamentos/{id}

Same body as POST (all editable fields). `id` and `created_at` do not change. Response `200` detail. Missing → `404`.

To delist: PUT the full resource with `disponible: false`.

## Layers

- `domain/entities/department.py`: entity + invariants.
- `application/use_cases/departments/`: one use case per file; in-memory adapters in `infrastructure/database/memory/` and `infrastructure/storage/memory/`.
- `infrastructure/database/postgres/` + Alembic.
- `infrastructure/http/departments.py` + `schemas.py`, mounted from `main.py` via `container.py`.
- Exception handlers: domain `422`, not found `404`.

## Checkpoints

- [x] Entity, port, use cases, SQLAlchemy repo, HTTP adapter + schemas
- [x] Domain invariants aligned with the HTTP schema
- [x] List uses the query builder (no `text()` / concatenated SQL)
- [x] Stable pagination (`created_at` desc, `id` desc) and `{ items, pagina, cantidad, total }`
- [x] `202` with detail; `404` on get/update; PUT is full replacement
- [x] Nullable `lat`/`lng`; more than 5 `imagenes` on POST → `422`
- [x] Tests: domain, create (in-memory), list filters (Postgres)

## How to test

With the Compose API (migrations applied):

- `POST /departamentos` valid body → `202` and detail with UUID `id`, `imagenes: []`, `consultas: []`
- `POST` with `precio` `0` or `moneda` `"EUR"` → `422`
- `POST` with invalid `imagenes` (not a data URL or http) → `422`
- `GET /departamentos?pagina=1&cantidad=10&precio_min=100000` → `200`, items with price ≥ 100000
- `GET /departamentos/{id}` missing → `404`
- `PUT /departamentos/{id}` full body and `disponible: false` → `200` and it is unavailable
- `pytest` for domain and application; list integration against Postgres

## Review

- The API container runs `alembic upgrade head` before uvicorn.
- Integration tests version the schema with Alembic (`upgrade head`), not `create_all`.
