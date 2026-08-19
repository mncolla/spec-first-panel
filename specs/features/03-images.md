# Feature: Images

status: done

## Goal

Several images per department, stored in MinIO. The list exposes the principal image and totals. The panel (and detail) survive if a URL does not resolve.

## Scope

**In**

- Department → images (`url`, order; principal = first)
- Server-side upload to MinIO on create (and on update when the set changes)
- Max 5 images (backend + contract)
- `BackgroundTasks` for upload so POST can return `202` quickly
- List: `imagen_principal`, `total_imagenes`
- Detail: image list
- Bucket created on startup if missing

**Out**

- Gallery UI (feature 09)
- 5-photo cap in the form (feature 08)
- Bulk photo seed (feature 06)

## Write contract

`imagenes` is still `list[str]` (same field as GET). Each item:

- data URL `data:image/jpeg|jpg|png|webp|gif;base64,...` → uploaded to MinIO
- `http(s)://...` URL → stored as-is (re-send GET URLs on PUT, or a broken URL)

Detail and list always expose public URLs (`S3_PUBLIC_ENDPOINT/{bucket}/{key}`).

## Checkpoints

- [x] `images` table (FK to `departments`; HTTP `imagenes`)
- [x] S3 client in `infrastructure/storage/s3/storage.py` targeting MinIO
- [x] Create uploads bytes and stores URLs
- [x] Reject more than 5
- [x] List and detail include principal image and totals
- [x] Update can replace the image set
- [x] Repository/integration test: department with N images + correct totals

## How to test

With the Compose API:

```bash
curl -s http://localhost:${API_PORT:-8000}/departamentos \
  -H 'Content-Type: application/json' \
  -d '{"titulo":"3 ambientes en Palermo","precio":180000,"moneda":"USD","metros_cuadrados":72.5,"direccion":"Av. Santa Fe 3500","imagenes":["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==","data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="]}'
```

- Create a department with 2 images → `202`; MinIO has 2 objects; detail lists them
- Create with 6 images → `422`
- List shows `total_imagenes: 2` and a non-null `imagen_principal`
- PUT with `imagenes: ["http://broken.example/x.jpg"]` then GET → `200` (the API does not check that the URL resolves)

## Review

- DB table `images` (English, like `departments`). JSON stays Spanish (`imagenes`).
- The `202` body already includes public URLs; `BackgroundTasks` runs `put`/`delete` after the response. `TestClient` waits for those tasks; curl may need a moment before the object is readable.
- `S3_PUBLIC_ENDPOINT` (`http://localhost:9000` in Compose) is what the browser uses; `S3_ENDPOINT` stays `http://minio:9000` on the Docker network.
- Bucket has a public-read policy. `try_ensure_bucket` on startup: if MinIO is down (local pytest), the API still boots.
- Cap of 5 MB per file (besides max 5 files). Types: jpeg, png, webp, gif.
