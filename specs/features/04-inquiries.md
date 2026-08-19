# Feature: Inquiries

status: done

## Goal

A department has many inquiries (name, email, message, date). Detail includes them; the list only includes the total.

## Scope

**In**

- `Inquiry` entity in `domain/entities/inquiry.py` (part of the `Department` aggregate)
- `inquiries` table (English; HTTP `consultas`)
- Detail: inquiry array ordered by date desc
- List: `total_consultas` (count, not N+1)
- Domain validation: email format, non-empty message

**Out**

- Public `POST /consultas` (not requested; write path is nested POST in [feature 11](11-create-inquiry.md))
- Dedicated inquiry UI (they show on detail, feature 09; the record form is feature 11)
- Bulk generation (feature 06)

## JSON contract (detail)

```json
"consultas": [
  {
    "nombre": "Ana Pérez",
    "email": "ana@example.com",
    "mensaje": "¿Sigue disponible?",
    "fecha": "2026-08-18T19:00:00Z"
  }
]
```

Order: `fecha` desc, `id` desc. Department PUT does not create or delete inquiries.

## Checkpoints

- [x] Model + relation on the aggregate
- [x] Get by id hydrates inquiries
- [x] List uses an aggregate count, not row load
- [x] Test: department with inquiries → detail returns them; list only the total

## How to test

There is no `POST /consultas`. Use the test fixture or SQL:

```bash
cd backend && uv run pytest tests/infrastructure/test_department_repository.py tests/api/test_departments.py -q
```

Or, with an existing department (`ID`):

```sql
INSERT INTO inquiries (id, department_id, name, email, message, created_at) VALUES
  (gen_random_uuid(), 'ID', 'Ana', 'ana@example.com', '¿Sigue disponible?', NOW()),
  (gen_random_uuid(), 'ID', 'Beto', 'beto@example.com', '¿Aceptan mascotas?', NOW() - interval '2 hours'),
  (gen_random_uuid(), 'ID', 'Cora', 'cora@example.com', 'Me interesa', NOW() - interval '1 day');
```

- `GET /departamentos/{id}` includes the 3 (Ana, Beto, Cora)
- `GET /departamentos` that item has `total_consultas: 3` and does not include the array

## Review

- Table `inquiries`, not `consultas`: same rule as `departments` / `images`.
- Relation uses `lazy="noload"` so the list cannot fire a row SELECT. Correlated count in the same query.
- PUT replaces photos and department fields; inquiries are preserved (they are not in the write body).
- Email: simple `local@domain.tld` regex. Name and message non-empty; max 120 / 4000.
