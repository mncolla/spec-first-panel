# Feature: Record inquiry

status: done

## Goal

The operator records an inquiry from an interested person on the department detail. Backend accepts a nested POST; the panel shows a form only when the department is available.

## Scope

**In**

- `Department.add_inquiry` on the aggregate (do not reuse `replace_inquiries` for a single add)
- Use case `create_inquiry` in `application/use_cases/`
- `POST /departamentos/{id}/consultas` → `201` with the created inquiry
- Domain: only `disponible = true`; otherwise `DomainError` → `422`
- Missing department → `404`
- Field rules: same as the `Inquiry` entity (name 1–120, email `local@domain.tld`, message 1–4000)
- Panel form on `/departamentos/:id` (nombre, email, mensaje) inside `features/departments/`; hidden until **Registrar nueva consulta**
- After `201`, the detail list refreshes (new inquiry first) and the list count can move
- RTL: available department accepts a submit; unavailable department does not show the form

**Out**

- `POST /consultas` as a top-level resource
- `consultas/` packages (backend or frontend)
- Auth / rate limit
- Creating inquiries on `disponible = false`
- Dedicated inquiry screen or route
- Changing or deleting inquiries

## JSON contract

`POST /departamentos/{id}/consultas`

Request:

```json
{
  "nombre": "Ana Pérez",
  "email": "ana@example.com",
  "mensaje": "¿Sigue disponible?"
}
```

| Field | Required | Notes |
|---|---|---|
| `nombre` | yes | 1–120 after trim |
| `email` | yes | `local@domain.tld` |
| `mensaje` | yes | 1–4000 after trim |

`fecha` is set by the server (UTC). The inquiry `id` is not in the HTTP JSON (same as feature 04).

Response `201`:

```json
{
  "nombre": "Ana Pérez",
  "email": "ana@example.com",
  "mensaje": "¿Sigue disponible?",
  "fecha": "2026-08-19T14:42:00Z"
}
```

Errors: unknown `{id}` → `404`. Invalid body or delisted department → `422`. No `409`.

## Checkpoints

- [x] `add_inquiry` appends, reorders by date desc, rejects unavailable
- [x] Use case persists via `DepartmentRepository.update`; in-memory test covers happy path + 404 + unavailable
- [x] HTTP: `201` shape; `404` / `422` as above
- [x] `GET /departamentos/{id}` includes the new row; list `total_consultas` increments without N+1
- [x] Detail form only when `disponible`; submitting/API error states
- [x] RTL: submit on an available department shows the inquiry in the list
- [x] No `consultas/` folder

## How to test

Backend (existing department `ID` with `disponible: true`):

```bash
curl -sS -D - -X POST "http://localhost:8000/departamentos/ID/consultas" \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana Pérez","email":"ana@example.com","mensaje":"¿Sigue disponible?"}'
```

- Status `201`, body has `nombre` / `email` / `mensaje` / `fecha`
- `GET /departamentos/ID` lists Ana first
- Same POST against a delisted department → `422`
- Unknown UUID → `404`

```bash
cd backend && uv run pytest tests/domain tests/application tests/api -q
cd frontend && npm test
```

Panel: open an available department → **Registrar nueva consulta** → fill the form → **Enviar** → the inquiry appears at the top of Consultas. The form is hidden again. Open a delisted one → the button is not there.

## Review

- Nested `POST /departamentos/{id}/consultas`, not `POST /consultas`. Inquiry stays on the `Department` aggregate (`add_inquiry`).
- Unavailable → `DomainError` / `422` (existing error map; no `409`).
- `201` returns only the created inquiry. The panel invalidates the detail and list queries; it does not require the full department in the POST body.
- `PostgresDepartmentRepository.update` now writes the inquiry collection (needed for this POST). PUT still preserves inquiries because `get` hydrates them and `Department.update` does not touch them.
- UI lives next to the existing list (`DepartmentInquiries` children); no new feature folder. Form only if `disponible`, collapsed behind **Registrar nueva consulta**. Submit is **Enviar**; **Cancelar** hides it. After a successful `201` it collapses again.
- Auth remains out of scope, same as the rest of the API.
