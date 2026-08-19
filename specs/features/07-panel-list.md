# Feature: Panel — list

status: done

## Goal

Paginated department table. Columns from the brief. Price, m², and availability filters. Loading / error / empty. CTA to create.

## Scope

**In**

- Feature `departments/`: list service + hooks (React Query)
- Table: ID, title, price (+ currency), principal thumbnail, photo count, inquiry count
- Placeholder if the thumbnail does not resolve
- Pagination aligned with the API (`pagina`, `cantidad`)
- Filters: price (min/max), square meters (min/max), available
- “Agregar Departamento” → `/departamentos/nuevo`
- Row click → `/departamentos/:id`
- Loading / error / empty

**Out**

- Create form (08)
- Detail screen (09)

## Checkpoints

- [x] List consumes `GET /departamentos` with pagination
- [x] Filters hit the API (not client-only)
- [x] Thumbnail placeholder on error
- [x] Price formatted with currency
- [x] Usable on small viewports
- [x] RTL test: table renders items from the mock / query

## How to test

With seed (06) and the Compose API:

```bash
docker compose up --build
cd frontend && npm run dev
```

Open http://localhost:5173

- See at least one page of results
- Filter `disponible=false` and `precio_min` → the table changes
- Stop the API → error message, not a blank screen
- Principal image 404 → placeholder, the row stays
- “Agregar Departamento” goes to `/departamentos/nuevo`

## Review

- API CORS (`CORS_ORIGINS`, default Vite 5173). The panel uses `VITE_API_URL` (default `http://localhost:8000`).
- Thumbnail is a 3:4 facade crop; on failure, a building placeholder.
- Filters apply on “Filtrar” (not on every keystroke) and reset to page 1.
- SQLAlchemy repository tests run against Compose Postgres inside a rolled-back transaction so they do not wipe the seed.
