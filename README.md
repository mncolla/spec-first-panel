# Lebane

Panel interno para una inmobiliaria: cargar, listar, filtrar y editar departamentos en venta. API FastAPI + React.

Este repo es, sobre todo, una **muestra de spec-driven development**: el producto se escribe antes que el código, se implementa **una feature a la vez**, y `done` no es “compila”.

![Panel Lebane](docs/panel.png)

**Demo:** [Railway](https://frontend-production-c4a83.up.railway.app) — `admin@lebane.local` / `lebanelebane`

---

## Cómo trabajo con specs

Tres documentos, no un ticket suelto:

| Doc | Pregunta que responde |
|---|---|
| [`specs/product.md`](specs/product.md) | Qué es el producto, In/Out, reglas, contrato HTTP, backlog |
| [`specs/architecture.md`](specs/architecture.md) | Cómo se construye (capas, stack, convenciones) |
| [`specs/features/NN-….md`](specs/features/) | Un recorte implementable, con checkpoints y cómo probarlo |

Si una idea choca con `product.md`, gana la spec. No se inventa DELETE físico, un segundo admin, ni paquetes inventados (`consultas/`, `imagenes/`).

El mismo ciclo está en [`.cursor/rules/spec-driven.mdc`](.cursor/rules/spec-driven.mdc): el agente (o yo) lee producto + arquitectura **antes** de tocar código, y trabaja una sola feature.

### Anatomía de una feature

Cada archivo en `specs/features/` tiene:

1. **`status`:** `created` → `in_progress` → `done` (la tabla de `product.md` se actualiza al mismo tiempo)
2. **Goal** — una frase
3. **In / Out** — el recorte. Out es tan importante como In
4. **Checkpoints** — criterios que se tildan en el mismo cambio, no “después”
5. **How to test** — comando que tiene que pasar
6. **Review** — decisiones que sobrevivieron al implementar (para no reabrirlas)

`done` solo si los checkpoints están cerrados **y** “How to test” funciona. Compilar no alcanza.

### Ciclo

```
1. product.md → feature in_progress
2. Implementar contra architecture.md
   backend hexagonal (código EN, HTTP ES) · frontend por features/ · tests junto al código
3. Tildar checkpoints · anotar Review
4. done + actualizar la tabla
5. Un commit Conventional Commit por cambio coherente
   feat(auth): …   no mezclar dos features
```

Ejemplo: [12-auth](specs/features/12-auth.md) define roles, JWT, `401`/`403` y qué **no** entra (OAuth, segundo admin). El código en `domain/entities/operator.py`, `application/use_cases/auth/` y `features/auth/` sigue ese recorte, no al revés.

El backlog también vive en specs: [14-panel-polish](specs/features/14-panel-polish.md) está `created` (filtros en URL, moneda, mapa en ficha). No es código a medias; es trabajo todavía no empezado.

---

## Qué construyen las specs

Inventario de departamentos. Sesión JWT (un **admin** único + **agentes**). Fotos en MinIO/S3. Consultas de interesados en la ficha. Dirección con Nominatim (coords persistidas). Seed de ≥ 500 filas.

Baja = `disponible = false`. No hay DELETE físico.

Contrato HTTP (español, como el brief). Código y tablas en inglés. El adapter HTTP es la anti-corruption layer.

Detalle de paths y JSON: [`product.md`](specs/product.md) y [feature 02](specs/features/02-departments-api.md).

---

## Stack

FastAPI · Python 3.12 · SQLAlchemy 2 · Alembic · React 19 · Vite · Tailwind 4 · TanStack Query · uv / Vitest.

Backend en capas (`domain` → `application` → `infrastructure`). Frontend por feature (`departments/`, `address/`, `auth/`). Las decisiones de diseño están en [`architecture.md`](specs/architecture.md), no solo en este README.

---

## Local

```bash
cp .env.example .env
docker compose up --build
```

Si Postgres quedó de una cadena Alembic vieja: `docker compose down -v && docker compose up --build`.

| Servicio | URL |
|---|---|
| API | http://localhost:8000 |
| OpenAPI | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Postgres | localhost:5432 (`lebane` / `lebane`) |
| MinIO | http://localhost:9000 · consola :9001 (`lebane` / `lebanelebane`) |

Panel:

```bash
cp frontend/.env.example frontend/.env
cd frontend && npm install && npm run dev
```

http://localhost:5173 → API en `:8000`. Sin sesión abre `/ingresar` (`admin@lebane.local` / `lebanelebane`).

Seed (≥ 500 deptos, fotos, consultas). No corre al arrancar:

```bash
docker compose exec api python -m app.seed
docker compose exec api python -m app.seed --force   # borra y vuelve a sembrar
```

### Tests

```bash
cd backend && uv sync --group dev && uv run pytest
cd backend && uv run ruff check .
cd frontend && npm test
```

Los tests de repo SQLAlchemy usan la Postgres de Compose en una transacción que se revierte: no borran el seed.

---

## Decisiones que salieron de las specs

- **Validación.** El brief pide tope de 5 fotos en el alta. El resto (título, precio, moneda) vive en dominio. Pydantic = tipos/`422`. `DomainError` también `422`.
- **Listado liviano.** `selectinload` de fotos, `noload` de consultas, `COUNT(*)` correlacionado. El detalle carga galería + consultas.
- **Storage.** Puerto `ObjectStorage`. MinIO local, S3-compatible. `POST /departamentos` → `202`; el upload puede ir en `BackgroundTasks`.
- **Dirección.** Nominatim en el browser (sin API key). El backend solo guarda `direccion`, `lat`, `lng`.
- **Auth.** JWT Bearer. `jti` = fila en `sessions`. Logout borra la fila. Admin desde env; agentes por `POST /operadores`.
- **Consultas.** Nested `POST /departamentos/{id}/consultas`. Solo si `disponible`. Comando del aggregate, no un paquete aparte.

---

## Railway

Cuatro servicios: Postgres, MinIO, API (`backend/Dockerfile`), frontend (`frontend/Dockerfile`). `VITE_API_URL` se hornea en el build.

Seed en el contenedor de la API (`railway ssh`), no con `railway run` (no resuelve `*.railway.internal`).

Variables y trampas de MinIO/`PORT` están comentadas en el historial del repo si hace falta replicar el deploy.

---

## Extra no incluido

E2E Playwright. Pulido de listado/mapa: [feature 14](specs/features/14-panel-polish.md).
