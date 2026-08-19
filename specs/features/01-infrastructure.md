# Feature: Local infrastructure

status: done

## Goal

Bring up API + PostgreSQL + MinIO with one command, and leave backend/frontend skeletons ready for product features.

## Scope

**In**

- Root `docker-compose.yml`: API, Postgres, MinIO (ports from env)
- Multistage backend Dockerfile
- Settings from environment variables
- API healthcheck
- Layered DDD skeleton: `app/domain/`, `app/application/`, `app/infrastructure/`
- Frontend entry in `src/app/` (providers + router)

**Out**

- Department endpoints
- Seed
- Domain tests

## Checkpoints

- [x] Compose starts Postgres + MinIO + API
- [x] `GET /health` returns `200 {"status": "ok"}`
- [x] MinIO reachable (console or boto3)
- [x] Backend reads `DATABASE_URL` and `S3_*` from env
- [x] Multistage Dockerfile builds the API
- [x] Vite starts with base routing (`/`)

## How to test

```bash
docker compose up --build
curl http://localhost:${API_PORT:-8000}/health
```

MinIO: open the console or list buckets. Front: `npm run dev`.

## Review

- MinIO healthcheck uses `mc ready local` (the image has no `curl`).
- MinIO tag is pinned (`RELEASE.2025-04-22T22-12-26Z`).
- `Settings` defaults to `localhost` for `fastapi dev` against Compose. Inside the API container, Compose overrides `DATABASE_URL` (`@db`) and `S3_ENDPOINT` (`http://minio:9000`).
