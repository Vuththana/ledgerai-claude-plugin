---
name: add-endpoint
description: Add one REST endpoint to a LedgerVision Spring Boot service — DTOs with dictionary validation, service logic with role and branch scope, controller, error codes and messages, and its tests. Use when asked to add or change an API endpoint.
argument-hint: "<METHOD /api/v1/path>"
---

# Add an endpoint

Endpoint: **$ARGUMENTS** (if empty: the next endpoint in the approved plan).

Its contract comes from the approved plan and the flow: method, path, who may call it, request and response fields, success status, and every error `code`. If any of these is missing, ask. Don't invent them.

## 1. DTOs (`<feature>/dto`)

- **Request DTO:** only the fields the client may send. Bean Validation straight from the dictionary:
  - Required `Y` → `@NotNull` / `@NotBlank`
  - `varchar` length → `@Size(max = n)`
  - Email → `@Email`
  - Enums → the Java enum type
  - Extra flow rules (password policy, code format) → a custom validator or a check in the service
- **Never accept protected fields from the client:** `user_id`, `business_id`, `role_id`, `is_active`, timestamps, `usd_equivalent`. A manager's `branch_id` is never accepted either.
- **Response DTO:** the dictionary field names via the global snake_case naming. Never secrets (`*_encrypted`, tokens, codes).

## 2. Service (`<feature>/service`)

1. **Role check.** Owner-only actions reject a manager with `403`.
2. **Scope.** Load with `business_id` (and `branch_id` for a manager) from the current user. Not found or out of scope → `404`.
3. **The flow's rules,** in the flow's order (the order decides which message the user sees).
4. **Money:** set `exchange_rate` from `businesses.exchange_rate`, and compute `usd_equivalent`.
5. **Writes** inside `@Transactional`. Map with ModelMapper, then set protected fields explicitly (`spring.md`).
6. **Side effects:** events after commit, audit and alert events, emails, Redis, as the plan says.
7. **Expected failures** → `ApiException(status, code, messageKey)`.

## 3. Controller (`<feature>/controller`)

- Path under `/api/v1`. `@Valid` on the request body. Get the current user from the security context.
- Thin: validate, call the service, return the DTO with the right status (`201` + body for a create, `204` with no body). See `spring.md` § JSON and API.

## 4. Messages

Add each new error `code`'s user message to `messages.properties`, in the flow's wording (`language.md`).

## 5. Tests

Follow the `write-tests` skill for this endpoint. It needs at least:

- the happy path, checking the response body and the database
- `400 VALIDATION_FAILED` with the right `field_errors` key
- each error `code` in the contract
- each role: owner, manager of the same branch, manager of another branch (`404` or `403`), deactivated user (`401`)

## 6. Check

`./gradlew build` passes. Give a `curl` example for the endpoint in the summary.
