# Data Dictionary

Every table and field of <Project>. Code, specs and plans use these names exactly. A change goes through a spec (its §8) and a docs pull request, never straight into code.

## Files

One file per domain. Add a row when you add a file.

| File | Tables |
|---|---|

## How a table is written

```markdown
## <table_name>

| Field Name | Datatype | Length | Required | PK/FK | Default | Reference | Description |
|---|---|---|---|---|---|---|---|
| `<table>_id` | uuid |  | Y | PK |  |  | auto generated |
| `<name>` | varchar | 50 | Y |  |  |  | unique per <scope>, ignoring letter case |
| `is_active` | boolean |  | Y |  | `true` |  | true = active<br>false = inactive |
| `created_at` | timestamp |  | Y |  | `current_timestamp` |  |  |
| `<parent>_id` | uuid |  | Y | FK |  | [<parent>](<file>.md#<parent>) |  |
```

- **Names:** snake_case, singular field names, plural table names.
- **Datatype:** `uuid`, `varchar` (with Length), `text`, `integer`, `numeric` (money, never float), `boolean`, `date`, `timestamp` (UTC), `enum` (list the values in Description), `jsonb` (describe its keys in `jsonb-shapes.md`).
- **Required:** `Y` means NOT NULL; empty means optional.
- **Rules** that aren't a type (unique, ranges, who may change it) go in Description.
