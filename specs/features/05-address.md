# Feature: Address autocomplete

status: done

## Goal

The address field is filled via Nominatim/OSM (no paid API key). Persist text + `lat`/`lng`.

## Scope

**In**

- `lat`, `lng` on the department (from feature 02)
- Front: `features/address/` autocomplete (debounce, suggestion list)
- On pick: set text + coordinates on the form
- README: how it works and why Nominatim (no key)

**Out**

- Provider calls from the backend
- Interactive map

## Checkpoints

- [x] Usable autocomplete (debounce ~300ms, loading / empty / error)
- [x] Pick persists `direccion`, `lat`, `lng` on create/update
- [x] API detail returns coordinates
- [x] No API key in env; documented
- [x] Nominatim usage policy respected (no hammering)
- [x] Picking a suggestion closes the list; typing again reopens it

## How to test

- On the create/edit form, type a CABA street → suggestions
- Pick one → POST/PUT sends text + lat/lng and the list closes
- GET detail shows the same coordinates
- Offline: the input shows an error and does not crash

## Review

- Nominatim from the browser: `fetch` cannot set `User-Agent`. We identify with `email` (`VITE_NOMINATIM_CONTACT`) + Referer. Debounce 300 ms, ≥ 3 characters, at most 1 request per second.
- A committed address (picked, or already saved on edit) does not trigger a new search until the operator types again.
