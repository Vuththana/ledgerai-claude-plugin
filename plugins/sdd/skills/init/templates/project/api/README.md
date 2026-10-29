# API Reference

Every endpoint, one file per service (`api/<service>.md`). The web front end builds against these entries, so an endpoint is listed here as soon as its contract is agreed (`📝 planned`), and updated when it's built (`🚧` on a branch, `✅` merged).

## Services

| Service | File |
|---|---|

## Response envelope (📝 proposed in TRD §3)

Every endpoint answers with:

| Field | On success | On error |
|---|---|---|
| `success` | `true` | `false` |
| `code` | The HTTP status name: `OK` or `CREATED` | A stable error code, e.g. `VALIDATION_FAILED`, never translated |
| `message` | A short user-safe message | A user-safe message, never exception text |
| `data` | The payload, fields named as in the dictionary | Field errors for `VALIDATION_FAILED`, else `null` or extra details |
| `timestamp` | ISO-8601, UTC | The same |

Shared errors every endpoint can return: `400 VALIDATION_FAILED`, `401` (not signed in), `403` (wrong role), `404` (not found or outside the caller's scope), `500 INTERNAL_ERROR`.

## How a service file is written

```markdown
# <service>

| Status | Method | Path | Who | Spec |
|---|---|---|---|---|
| 📝 | POST | /api/v1/<things> | Owner | [<feature>](../specs/<feature>/spec.md) ABC-R01 |

### POST /api/v1/<things>

Body: `<field>` (required, max 50), … `201 CREATED`, `data`: the **<thing>**.

| Status | `code` | When |
|---|---|---|
| 409 | `<THING>_TAKEN` | <when> (ABC-M01) |
```
