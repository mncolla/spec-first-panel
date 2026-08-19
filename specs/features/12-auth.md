# Feature: Authentication and roles

status: done

## Goal

The panel is an internal tool for a real-estate shop: one **admin** and **agentes inmobiliarios**. Login issues a Bearer JWT; every department route requires a valid session. Logout revokes the session on the server.

## Scope

**In**

- `Operator` entity (`domain/entities/operator.py`): email, password hash, role `admin` | `agent`
- Unique admin: at most one `admin`. Bootstrap from env if none exists (`OPERATOR_EMAIL`, `OPERATOR_PASSWORD`)
- Tables `operators` and `sessions` (English). HTTP Spanish (`sesion`, `clave`, `rol`)
- Ports: password hasher + token issuer in `application/ports/`. Implementations in `infrastructure/security/`
- Use cases in `application/use_cases/auth/` (`login`, `logout`, `get_current_operator`) and `application/use_cases/operators/` (`create_operator`: admin creates an `agent` only)
- HTTP adapter `infrastructure/http/session.py` (+ operator write). Department handlers take `Depends(require_operator)`; they do not take a user into the department use cases
- `POST /sesion` → `200` `{ email, rol, token }`
- `GET /sesion` → `200` `{ email, rol }` or `401`
- `DELETE /sesion` → `204`; deletes the session row so the JWT stops working
- `POST /operadores` (admin) → `201` `{ email, rol }`. Body `rol` must be `agente`
- Protect all `/departamentos*` (GET included). `/health` and seed CLI stay public
- Panel: `features/auth/`, route `/ingresar`, Bearer on `lib/api.ts`, `401` → login
- Shell: email, role label, **Cerrar sesión**
- RTL: unauthenticated visitor sees the login form; a successful login reaches the list

**Out**

- Public signup / forgot password / OAuth / refresh tokens
- Second admin
- Operator list/edit/delete UI (create-agent is API-only in this feature)
- Cookie / CSRF
- Rate limit
- Finer permissions (both roles run the current panel; only admin creates agents)
- Public listing site

## Roles

| Domain | HTTP `rol` | Who | Can |
|---|---|---|---|
| `ADMIN` | `admin` | Unique shop owner (env bootstrap) | Full panel + `POST /operadores` |
| `AGENT` | `agente` | Agente inmobiliario (day-to-day listings and inquiries) | Full panel (departments + consultas). Cannot create operators (`403`) |

`vendedor` is not a role name: the person who already uses this panel is an **agente inmobiliario**.

Unauthenticated → `401`. Authenticated but not allowed (`agente` hitting `POST /operadores`) → `403`.

## JSON contract

Backend paths and keys (Spanish). The panel route `/ingresar` is frontend only; it calls `POST /sesion`.

### POST /sesion

Request:

```json
{
  "email": "admin@lebane.local",
  "clave": "secret-password"
}
```

Response `200`:

```json
{
  "email": "admin@lebane.local",
  "rol": "admin",
  "token": "<jwt>"
}
```

Unknown email or wrong password → `401` (same message, no user enumeration). Invalid body → `422`.

### GET /sesion

Header `Authorization: Bearer <jwt>`. Response `200`: `{ "email", "rol" }`. Missing/invalid/revoked/expired → `401`.

### DELETE /sesion

Header `Authorization: Bearer <jwt>`. Response `204` empty body. The session row is deleted; the same token then gets `401`. Missing token → `401`.

### POST /operadores (admin)

Request:

```json
{
  "email": "agente@lebane.local",
  "clave": "otra-clave",
  "rol": "agente"
}
```

Response `201`: `{ "email": "agente@lebane.local", "rol": "agente" }`.

`rol: "admin"` → `422`. Duplicate email → `422`. Caller is `agente` → `403`. No Bearer → `401`.

## Checkpoints

- [x] Operator invariants: email format, non-empty password hash, unique admin
- [x] Login creates a `sessions` row and a JWT whose `jti` is that id; logout deletes the row
- [x] `require_operator` on every `/departamentos*` handler; tests that omit the header get `401`
- [x] Bootstrap creates the admin once from env; a second admin cannot be inserted
- [x] `POST /operadores` as admin → agent; as agent → `403`
- [x] `GET /health` still `200` without a token
- [x] Panel `/ingresar`; token in versioned `sessionStorage`; api client sends Bearer
- [x] RTL: login success lands on the list; 401 on a department call redirects to `/ingresar`

## How to test

```bash
# no token
curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8000/departamentos
# 401

curl -sS -X POST http://localhost:8000/sesion \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@lebane.local","clave":"<OPERATOR_PASSWORD>"}'
# 200 + token

curl -sS -X DELETE http://localhost:8000/sesion \
  -H "Authorization: Bearer TOKEN"
# 204; same token on GET /sesion → 401
```

Panel: open `/` without session → `/ingresar`. Sign in as admin → inventory. Cerrar sesión → login again. Create an agent via `POST /operadores`, sign in as that agent → panel works, `POST /operadores` → `403`.

```bash
cd backend && uv run pytest tests/domain tests/application tests/api -q
cd frontend && npm test
```

## Review

- `/sesion` + `clave` are the HTTP contract (backend). `/ingresar` is the panel route (frontend). Both exist; they are not the same layer.
- Bearer JWT (HS256). Not a cookie. Logout is not client-only: `sessions` + JWT `jti` so `DELETE /sesion` revokes.
- Hasher is PBKDF2-HMAC-SHA256 in the stdlib (`infrastructure/security/password_hasher.py`), not bcrypt: no extra native dep, same port.
- Department use cases stay unaware of operators. Auth is a driving-adapter dependency.
- Hasher and token issuer are application ports; PBKDF2/JWT stay in `infrastructure/security/`.
- Existing department API tests must send a Bearer (test helper) or override `require_operator`.
