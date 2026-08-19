# Feature: Create agent from the panel

status: done

## Goal

The unique **admin** manages operators from the panel: sees the existing list and creates an **agente**. Same `POST /operadores` as feature 12; list is `GET /operadores`.

## Scope

**In**

- Panel route `/operadores` in `features/auth/` (layout aligned with inventario: `max-w-6xl`, table + form)
- Table of operators: email + rol (never password hash)
- Form: email + clave (min 8). `rol` is always `agente` (not a field)
- Shell link **Operadores** only if `rol === admin`
- Agent hitting the route: message, no table/form (API would be `403`)
- `GET /operadores` (admin) → `{ items: [{ email, rol }] }`
- README: public demo URL

**Out**

- Edit / delete operators
- Second admin
- Invite email / forgot password

## Checkpoints

- [x] Admin opens `/operadores`, sees the table and submits valid email+clave → success and the new email is shown
- [x] Agent does not see **Operadores**; the route does not show the table or form
- [x] Empty form shows the same validation as login (email, clave ≥ 8)
- [x] `GET /operadores` as admin → list without hashes; as agent → `403`; no token → `401`
- [x] README has the demo URL

## How to test

```bash
cd backend && uv run pytest tests/api/test_session.py tests/application/test_auth.py
cd frontend && npm test
```

Panel: sign in as admin → **Operadores** → table includes the admin → create `agente@lebane.local` / clave ≥ 8 → success and the row appears. Sign out, sign in as that agent → inventory works, no **Operadores**.

## Review

- `GET /operadores` returns `{ items: [{ email, rol }] }`. Hashes never leave the adapter.
- The panel never sends `rol: "admin"`.
- Operator UI lives in `features/auth/`, not a new `operadores/` package.
- `/operadores/nuevo` still renders the same screen (bookmark).
