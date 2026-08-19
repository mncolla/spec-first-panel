# Product — Department panel (Lebane)

Internal admin panel for a real-estate operator: create, list, filter, and edit apartments for sale.

REST API (FastAPI) + panel (React). Product quality, not a prototype.

## User

Lebane operator. Auth is out of scope for this delivery.

## Scope

**In**

- Department CRUD (create, list, detail, update)
- Images in S3-compatible object storage (MinIO locally)
- Inquiries on a department (name, email, message, date)
- Address autocomplete with persisted coordinates
- Seed of ≥ 500 departments
- Panel: list, create, detail/edit, filters
- Backend and frontend tests; README with decisions

**Out**

- Authentication / roles
- Physical DELETE (delisting is `disponible = false`)
- Public inquiry endpoint (the operator reads them on the detail; seed loads them)
- Cloud deploy (optional extra, feature 10)

## Product rules

The brief only requires a 5-photo cap on create (frontend). The rest is ours:

| Field | Rule |
|---|---|
| `titulo` | required, 3–120 characters |
| `descripcion` | optional, max 4000 |
| `precio` | required, `> 0` |
| `moneda` | `USD` or `ARS` |
| `metros_cuadrados` | required, `> 0` |
| `direccion` | required (autocomplete text) |
| `disponible` | boolean, default `true` |
| `imagenes` | 0–5 on create; the backend rejects more than 5 |
| Delist / relist | `disponible` + PUT only; no DELETE |

## API contract (summary)

HTTP paths and JSON keys follow the brief (Spanish). Code and database are English.

- Identifier: UUID (`id` in the URL and JSON).
- `POST /departamentos` → `202 Accepted` with the detail resource in the body. `202` stays even after images move to background work (feature 03).
- `GET /departamentos` → `200` paginated + filters `disponible`, `precio_min`, `precio_max`, `metros_min`, `metros_max`.
- `GET /departamentos/{id}` → `200` (detail) or `404`.
- `PUT /departamentos/{id}` → `200` (detail) or `404`. Full replacement of editable fields (same body as POST). No PATCH or DELETE.

Pagination: `pagina` (from 1, default 1), `cantidad` (default 20, max 100). Envelope `{ items, pagina, cantidad, total }`. Stable order: `created_at` desc, `id` desc.

List items include `imagen_principal`, `total_imagenes`, and `total_consultas`.
Detail: full department + `imagenes` + `consultas`.

`lat` / `lng` are optional (`direccion` text is required). The price filter does not split by currency.

JSON shapes live in [feature 02](features/02-departments-api.md).

## Features

| # | Feature | Status |
|---|---|---|
| 01 | [Infrastructure](features/01-infrastructure.md) | done |
| 02 | [Departments API](features/02-departments-api.md) | done |
| 03 | [Images](features/03-images.md) | done |
| 04 | [Inquiries](features/04-inquiries.md) | done |
| 05 | [Address](features/05-address.md) | done |
| 06 | [Seed](features/06-seed.md) | done |
| 07 | [Panel list](features/07-panel-list.md) | done |
| 08 | [Panel create](features/08-panel-create.md) | done |
| 09 | [Panel detail and edit](features/09-panel-detail.md) | done |
| 10 | [Quality](features/10-quality.md) | done |

Statuses: `created` · `in_progress` · `done`. Update this table when a feature changes status.

## How we work

One feature at a time. `done` only when checkpoints are closed and “How to test” works.

Commits: [Conventional Commits](https://www.conventionalcommits.org/). Format `type(scope): summary`.

| Type | When |
|---|---|
| `feat` | new behavior |
| `fix` | bug fix |
| `docs` | specs, README, comments |
| `refactor` | internal change, same behavior |
| `test` | tests only |
| `chore` | deps, Compose, tooling |

Scope = module or feature (`infra`, `departments`, `images`, `inquiries`, `address`, `seed`, `panel`). One commit = one coherent change; do not mix features.
