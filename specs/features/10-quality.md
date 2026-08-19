# Feature: Quality and delivery

status: done

## Goal

Match the brief’s delivery bar: tests, README, decisions, clean code. Cloud deploy is an optional extra.

## Scope

**In**

- Backend: endpoint/validation unit tests + httpx integration
- Frontend: RTL for the 5-photo cap (08) and detail (09)
- Backend tooling: ruff
- Root README: install, `docker compose`, Nominatim env, how to test, decisions (validation, storage, data access, 202 + background)
- Repo ready to invite `LebaneRecruiting`

**Out (optional extra)**

- Playwright E2E: create + edit + view
- Cloud deploy + URL in the README

## Checkpoints

- [x] `pytest` documented and reproducible
- [x] Frontend tests for 5 photos and detail pass
- [x] README covers Compose + MinIO + address + tests + decisions
- [x] OpenAPI `/docs` matches the contract
- [x] No leftover example fetches; health is not the only proof of value
- [ ] (Optional) E2E
- [ ] (Optional) Demo URL

## How to test

```bash
docker compose up --build
cd backend && uv run pytest
cd frontend && npm test
```

Read the README from scratch (fresh clone) and follow it without improvising.

## Review

- Root README covers Compose, seed, Nominatim, tests, and decisions (validation, MinIO, hexagonal, 202 + background).
- `ruff` is a dev extra (`uv run ruff check .`). E2E and deploy stay out of this delivery.
