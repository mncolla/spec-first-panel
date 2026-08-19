# Feature: Panel — detail and edit

status: done

## Goal

Dedicated screen (not a drawer/modal) with the department, gallery, and in-place edit via PUT. Inquiries are listed. Broken images do not break the view.

## Scope

**In**

- Route `/departamentos/:id`
- GET detail: data + gallery + inquiries
- Edit the same fields as create (including available = delist/relist)
- PUT on save
- API 404 → not-found screen
- RTL test: opening detail shows the right info (title, price, etc.)

**Out**

- Creating inquiries from the panel
- Playwright E2E (optional in 10)

## Checkpoints

- [x] Navigation from a list row
- [x] Gallery with placeholder per broken image
- [x] Edit form prefilled
- [x] Save calls PUT and reflects changes
- [x] Inquiry list (name, email, message, date)
- [x] Test: detail opens with the correct info

## How to test

- Click a row → URL `/departamentos/:id`, data matches the API
- Edit title and `disponible` → PUT 200 → reload shows the new values
- Missing department → not found
- Photo 404 → gallery placeholder

## Review

- Dedicated page, not a drawer. API 404 → “No encontramos ese departamento”. Unchecking available is delisting.
- PUT sends the full photo list (existing URLs + new data URLs).
