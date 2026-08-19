# Feature: Panel — create

status: done

## Goal

Create form. Max 5 photos (the only rule the brief requires). Address autocomplete (05).

## Scope

**In**

- Route `/departamentos/nuevo`
- Fields: title, address (autocomplete), price, currency, availability, m², up to 5 photos
- Front validation: no more than 5 photos (disable input + message)
- `product.md` rules in the form (UX); the backend remains the source of truth
- Submit → `POST /departamentos` → redirect to detail
- Submitting / API error states

**Out**

- Edit (09)
- Detail gallery

## Checkpoints

- [x] Cannot attach more than 5 photos (RTL test required)
- [x] Address uses `features/address`
- [x] Per-field validation errors
- [x] API 422 mapped onto the form
- [x] After success, the department exists on list/detail

## How to test

- Try 6 photos → blocked in the UI, test green
- Submit empty → errors
- Valid create with 2 photos and a picked address → `202` and the resource exists
- API down → error, the form is not silently lost

## Review

- The form lives in `departments/` and is reused on 09. Photos go as data URLs (contract 03). After `202` it redirects to `/departamentos/:id`.
- The operator must pick a Nominatim suggestion: typing a street without selecting does not send `lat`/`lng`.
