# Feature: Seed

status: done

## Goal

≥ 500 varied departments, each with 0–8 images and 0–40 inquiries. Seed images live in MinIO.

## Scope

**In**

- Opt-in seed command (`python -m app.seed`), not silent on API boot
- Heterogeneous data: prices, currencies, m², availability, CABA/AMBA addresses, titles
- Images uploaded to MinIO (not only broken URLs; some invalid URLs on purpose for UI resilience)
- Inquiries with spread dates

**Out**

- UI
- Destructive re-seed without an explicit flag

Note: the brief allows 0–8 images in seed; product create is capped at 5. Seed may exceed 5 for list/detail; HTTP POST stays at 5.

## Checkpoints

- [x] Command documented in the README
- [x] `COUNT(*)` departments ≥ 500
- [x] Mix of available / unavailable, USD / ARS, 0 and N images/inquiries
- [x] Objects in the MinIO bucket
- [x] `GET /departamentos?cantidad=50` stays responsive

## How to test

```bash
docker compose exec api python -m app.seed
# if data already exists (e.g. from Swagger):
docker compose exec api python -m app.seed --force
```

```bash
docker compose exec db psql -U lebane -d lebane -c 'SELECT COUNT(*) FROM departments;'
curl -s -o /dev/null -w '%{http_code} %{time_total}\n' 'http://localhost:8000/departamentos?pagina=1&cantidad=50'
```

- Check counts in Postgres
- List bucket `departments` in MinIO (console :9001)
- `GET /departamentos?pagina=1&cantidad=50` < 500ms on a reasonable local setup
- Without `--force`, a second run does not overwrite the catalog

## Review

- CLI `python -m app.seed`; it does not run when the container starts.
- `--force` deletes departments (cascade images/inquiries). Without the flag: empty → insert; ≥ 500 → skip; 1–499 → refuse.
- The aggregate allows up to 8 photos (`MAX_SEEDED_IMAGES`); HTTP create/update stay at 5 (`MAX_IMAGES`).
- 1×1 PNG placeholders in MinIO; ~12% of departments with photos get a broken URL (`invalid.lebane.local`) for the panel.
- `--force` does not sweep orphan MinIO objects (acceptable locally).
