# Product — Department panel (Lebane)

Internal admin panel for a real-estate operator: create, list, filter, and edit apartments for sale.

REST API (FastAPI) + panel (React). Product quality, not a prototype.

## User

Lebane **admin** (unique) and **agentes inmobiliarios**. They share the inventory panel; only admin can create agents.

## Scope

**In**

- Department CRUD (create, list, detail, update)
- Images in S3-compatible object storage (MinIO locally)
- Inquiries on a department (name, email, message, date)
- Operator records an inquiry from an interested person (panel form + nested POST)
- Authentication: Bearer JWT session, unique admin + agentes
- Address autocomplete with persisted coordinates
- Seed of ≥ 500 departments
- Panel: list, create, detail/edit, filters
- Backend and frontend tests; README with decisions

**Out**

- Physical DELETE (delisting is `disponible = false`)
- Public listing site or top-level `POST /consultas`
- Inquiries on a delisted department (`disponible = false`)
- Public signup, password reset, OAuth, a second admin
- Rate limit
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
| `nombre` (inquiry) | required, 1–120 |
| `email` (inquiry) | required, `local@domain.tld` |
| `mensaje` (inquiry) | required, 1–4000 |
| Record inquiry | only if `disponible = true` |
| Auth | Bearer JWT; `/departamentos*` requires a session |
| `rol` | `admin` (unique) or `agente` |

## API contract (summary)

HTTP paths and JSON keys follow the brief (Spanish). Code and database are English.

- Identifier: UUID (`id` in the URL and JSON).
- `POST /departamentos` → `202 Accepted` with the detail resource in the body. `202` stays even after images move to background work (feature 03).
- `GET /departamentos` → `200` paginated + filters `disponible`, `precio_min`, `precio_max`, `metros_min`, `metros_max`.
- `GET /departamentos/{id}` → `200` (detail) or `404`.
- `PUT /departamentos/{id}` → `200` (detail) or `404`. Full replacement of editable fields (same body as POST). No PATCH or DELETE.
- `POST /departamentos/{id}/consultas` → `201` with the created inquiry (`nombre`, `email`, `mensaje`, `fecha`). `404` if the department is missing. `422` if the body is invalid or the department is not available. No PATCH/DELETE on inquiries.
- `POST /sesion` → `200` `{ email, rol, token }`. `GET /sesion` → `200` or `401`. `DELETE /sesion` → `204` (revokes). `GET /operadores` (admin) → `{ items: [{ email, rol }] }`. `POST /operadores` (admin) → `201` agent. Unauthenticated department calls → `401`. Agent listing or creating operators → `403`.

Pagination: `pagina` (from 1, default 1), `cantidad` (default 20, max 100). Envelope `{ items, pagina, cantidad, total }`. Stable order: `created_at` desc, `id` desc.

List items include `imagen_principal`, `total_imagenes`, and `total_consultas`.
Detail: full department + `imagenes` + `consultas`.

`lat` / `lng` are optional (`direccion` text is required). The price filter does not split by currency.

JSON shapes live in [feature 02](features/02-departments-api.md) (departments), [feature 11](features/11-create-inquiry.md) (inquiry write), and [feature 12](features/12-auth.md) (session). Admin creates agents from the panel in [feature 13](features/13-create-agent.md).

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
| 11 | [Record inquiry](features/11-create-inquiry.md) | done |
| 12 | [Auth and roles](features/12-auth.md) | done |
| 13 | [Create agent from the panel](features/13-create-agent.md) | done |
| 14 | [Panel list and map polish](features/14-panel-polish.md) | created |

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

Scope = module or feature (`infra`, `departments`, `images`, `inquiries`, `address`, `seed`, `panel`, `auth`). One commit = one coherent change; do not mix features.
