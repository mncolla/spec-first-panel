# Lebane — Panel de departamentos

Prueba técnica: API FastAPI + panel React para una inmobiliaria. Specs en [`specs/product.md`](specs/product.md) y [`specs/architecture.md`](specs/architecture.md).

El operador carga, lista, filtra y edita departamentos en venta. No hay autenticación ni DELETE físico: la baja es `disponible = false`.

<img width="1920" height="1440" alt="238_1x_shots_so" src="https://github.com/user-attachments/assets/d4a98112-62ab-4658-ad63-fffb3f546702" />


## Local

Copiá el env de ejemplo y levantá Postgres, MinIO y la API:

```bash
cp .env.example .env
docker compose up --build
```

Si Postgres quedó de una cadena Alembic anterior, recreá el volumen: `docker compose down -v && docker compose up --build`.

| Servicio | URL |
|---|---|
| API | http://localhost:8000 |
| OpenAPI | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Postgres | localhost:5432 (`lebane` / `lebane`) |
| MinIO API | http://localhost:9000 |
| MinIO consola | http://localhost:9001 (`lebane` / `lebanelebane`) |

Panel:

```bash
cp frontend/.env.example frontend/.env
cd frontend && npm install && npm run dev
```

http://localhost:5173 habla con la API en `:8000` (CORS habilitado). `VITE_API_URL` cambia el origin si hace falta.

### Seed

Carga ≥ 500 departamentos con fotos en MinIO y consultas. No corre al arrancar.

```bash
docker compose exec api python -m app.seed
```

Si ya hay departamentos (menos de 500), el comando se niega. Para borrar y volver a sembrar:

```bash
docker compose exec api python -m app.seed --force
```

## Dirección (Nominatim)

El autocompletado corre **en el navegador**, contra Nominatim/OSM. El backend solo persiste `direccion`, `lat` y `lng`. No hay API key paga.

Por qué Nominatim: cubre CABA sin contrato, sin billing, y el enunciado no pide un proveedor comercial.

Política de uso:

- Identificación: query `email` con `VITE_NOMINATIM_CONTACT` (el browser no deja setear `User-Agent` en `fetch`). Nominatim también ve el `Referer`.
- Debounce 300 ms, mínimo 3 caracteres, y no más de 1 request por segundo.
- `countrycodes=ar`, idioma `es`, tope 5 sugerencias.

Sin red, el input muestra error y no crashea. Hay que elegir una sugerencia para mandar coordenadas (texto libre sin seleccionar no alcanza).

## Tests

```bash
cd backend && uv sync --group dev && uv run pytest
cd backend && uv run ruff check .
cd frontend && npm test
```

Los tests de repositorio SQLAlchemy usan la Postgres de Compose, pero cada caso corre en una transacción que se revierte: no borra el seed del panel.

## Contrato HTTP (resumen)

Español, como el PDF. IDs UUID.

| Método | Path | Status |
|---|---|---|
| POST | `/departamentos` | `202` + detalle |
| GET | `/departamentos` | `200` paginado |
| GET | `/departamentos/{id}` | `200` o `404` |
| PUT | `/departamentos/{id}` | `200` o `404` |

Paginación: `pagina` ≥ 1, `cantidad` default 20 máx. 100. Filtros: `disponible`, `precio_min`, `precio_max`, `metros_min`, `metros_max`.

`POST` queda en `202` aunque la fila ya esté persistida: las imágenes se suben a MinIO en `BackgroundTasks`. El body ya trae el recurso. `PUT` es reemplazo completo (mismos campos que el alta). No hay PATCH ni DELETE.

Fotos de escritura: data URL (`data:image/jpeg\|png\|webp\|gif;base64,...`) o URL `http(s)`. Máximo 5.

Detalle de JSON: [`specs/features/02-departments-api.md`](specs/features/02-departments-api.md).

## Decisiones

**Validación.** El enunciado exige tope de 5 fotos en el alta (también en el front, con test RTL). El resto vive en dominio (`titulo` 3–120, `precio` > 0, moneda `USD`/`ARS`, etc.). Pydantic cubre tipos/`422`. `DomainError` también es `422`.

**Storage.** MinIO S3-compatible local. El front manda bytes (data URL) o URLs ya públicas. El backend sube a un bucket `departments` y devuelve URLs con `S3_PUBLIC_ENDPOINT`. Una URL rota no tumba el panel: hay placeholder.

**Acceso a datos.** Backend hexagonal / DDD por capas: entidades y contratos de repositorio en `domain/`, casos de uso en `application/`, adapters por tecnología en `infrastructure/` (`database/postgres`, `storage/s3`, `http`). El `container` arma las dependencias. HTTP en español, código en inglés. Sin SQL concatenado. Frontend por features (`departments/`, `address/`).

**Ruteo del panel.** wouter. `/` listado, `/departamentos/nuevo` alta, `/departamentos/:id` ficha + edición.

**Consultas.** El operador las registra en el detalle (`POST /departamentos/{id}/consultas` → `201`) solo si el departamento está disponible. El seed también carga historial. No hay `POST /consultas` suelto ni auth.

## Stack

FastAPI 0.14x, Python 3.12, SQLAlchemy 2, Alembic, React 19, Vite, Tailwind 4, TanStack Query, Vitest.

## Railway

Un proyecto, cuatro servicios:

| Servicio | Origen | Notas |
|---|---|---|
| Postgres | plugin de Railway | `DATABASE_URL` (el backend lo pasa a `postgresql+psycopg://`) |
| MinIO | imagen `minio/minio` + volume en `/data` | start: `minio server /data --address :$PORT` |
| API | `backend/` (`Dockerfile`) | `PORT` lo pone Railway |
| Frontend | `frontend/` (`Dockerfile`) | `VITE_API_URL` se hornea en el build |

Variables (referencias entre servicios):

```
# API
DATABASE_URL=${{Postgres.DATABASE_URL}}
S3_ENDPOINT=http://${{MinIO.RAILWAY_PRIVATE_DOMAIN}}:${{MinIO.PORT}}
S3_PUBLIC_ENDPOINT=https://${{MinIO.RAILWAY_PUBLIC_DOMAIN}}
S3_ACCESS_KEY=<mismo MINIO_ROOT_USER>
S3_SECRET_KEY=<mismo MINIO_ROOT_PASSWORD>
S3_BUCKET=departments
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}

# Frontend (build)
VITE_API_URL=https://${{Api.RAILWAY_PUBLIC_DOMAIN}}
VITE_NOMINATIM_CONTACT=<email de contacto Nominatim>
```

MinIO: `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` (≥ 8 caracteres) y un volume montado en `/data`. Generá dominio público para API, frontend y MinIO (las fotos se cargan desde el browser).

Seed una vez que la API esté arriba:

```bash
railway run -s api -- python -m app.seed
```

## Extra no incluido

Auth y E2E Playwright. Si hay demo, la URL va acá.
