# Feature: Panel list and map polish

status: created

## Goal

Make the inventory easier to scan: clearer price filters (including currency), text search, and a map on the ficha when coordinates exist.

## Scope

**In**

- Filter placeholders (`100000`) and a short note that USD and ARS share the same numeric range
- Filter by `moneda` (`USD` | `ARS` | all). API query `moneda`, AND with the existing filters
- Search by `titulo` and `direccion` (one text box, case-insensitive, API query `q`)
- Map on the department detail when `lat` / `lng` are present (OpenStreetMap, no paid key). Missing coords → no map, ficha still works

**Out**

- FX conversion / dual price columns
- Drawing search radius / polygon
- Changing how price is stored

## Checkpoints

- [ ] Placeholders and the USD/ARS mix line are visible on the list
- [ ] `GET /departamentos?moneda=USD` returns only USD rows
- [ ] `GET /departamentos?q=` matches title or address
- [ ] Detail with coords shows a map; without coords it does not crash
- [ ] RTL: list request includes the new query params; detail map is present when lat/lng exist

## How to test

```bash
cd backend && uv run pytest tests/api/test_departments.py tests/application -q
cd frontend && npm test
```

Panel: filter moneda USD; search a barrio from the seed; open a ficha with coordinates and see the map.

## Review

- Price filter still does not convert currencies. `moneda` is an extra equality filter.
- Search is a driving-adapter query param mapped to SQLAlchemy `ilike`, not `text()`.
- Map is frontend-only; the backend already persists `lat` / `lng`.
