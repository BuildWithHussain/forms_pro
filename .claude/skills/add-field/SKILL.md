---
name: add-field
description: Add a new field type to Forms Pro end-to-end (backend doctype, Python mapping, submission handling, frontend component, fieldTypes registry, options resolution, and submission display).
argument-hint: <FieldtypeName> e.g. "Signature"
---

You are adding a new field type to Forms Pro. The field type name is: **$ARGUMENTS**

Work through each step below in order. Commit in three logical batches at the end (backend doctype, backend submission, frontend).

---

## Step 1 — Understand the codebase conventions

Read the following files before making any changes so you understand the patterns:

- `forms_pro/forms_pro/doctype/form_field/form_field.py` — `FORM_TO_FRAPPE_FIELDTYPE` dict and `DF.Literal` type hint block
- `forms_pro/forms_pro/doctype/form_field/form_field.json` — the `fieldtype` Select field's `options` string
- `frontend/src/types/FormsPro/form_field.types.ts` — `Fieldtype` enum
- `frontend/src/config/fieldTypes.ts` — `FIELD_TYPE_DEFINITIONS` array
- `frontend/src/utils/selectOptions.ts` — `getFieldOptions` function
- `frontend/src/components/form/submissions/SubmissionFieldValue.vue` — submission display cases
- `forms_pro/api/submission.py` — `submit_form_response` and `_validate_form_response`

---

## Step 2 — Backend: doctype

**`forms_pro/forms_pro/doctype/form_field/form_field.json`**
- Add `\n<FieldtypeName>` to the end of the `options` string of the `fieldtype` Select field.
- Update the `modified` timestamp to today's date.

**`forms_pro/forms_pro/doctype/form_field/form_field.py`**
- Add an entry to `FORM_TO_FRAPPE_FIELDTYPE`:
  ```python
  "<FieldtypeName>": {"fieldtype": "<FrappeFieldtype>"},
  ```
  Choose the appropriate Frappe fieldtype. Common mappings:
  - Scalar text → `"Data"` or `"Small Text"`
  - Multi-value JSON array → `"JSON"`
  - Boolean → `"Check"`
  - Number → `"Int"` or `"Float"`
- Add `"<FieldtypeName>"` to the `DF.Literal[...]` type hint list inside the `TYPE_CHECKING` block.

---

## Step 3 — Backend: submission serialization

Open `forms_pro/api/submission.py` and check whether the new field's value type could arrive as a Python `list` from Frappe's request deserialization (this happens for `JSON` array fields like Multiselect).

If yes, the existing guard in `submit_form_response` already handles it:
```python
if isinstance(value, list):
    value = json.dumps(value)
```
No change needed there.

Also check `_validate_form_response`: if an empty value for the new field type can be represented as something other than `None`/`""`/`[]` (e.g. an empty dict `{}`), add it to the `is_empty` check:
```python
is_empty = value is None or value == "" or value == [] or ...
```

---

## Step 4 — Frontend: types

**`frontend/src/types/FormsPro/form_field.types.ts`**
- Add the new enum member to `Fieldtype`:
  ```ts
  "<SCREAMING_SNAKE>" = "<FieldtypeName>",
  ```
  The enum key must be SCREAMING_SNAKE_CASE; the value must exactly match the Python/JSON string.

---

## Step 5 — Frontend: Vue component

Create `frontend/src/components/fields/<FieldtypeName>.vue`.

Contract the component must follow:
- `v-model` / `defineModel` for the field value (type depends on the field — `string`, `string[]`, `number`, etc.)
- `options?: string[]` prop if the field consumes options (like Select or Multiselect)
- `disabled?: boolean` prop for read-only mode in submission view / edit mode preview

If you are writing a scaffold (placeholder), keep it minimal but functional — render the value in read mode and a basic input in edit mode. The user will replace it with the real component.

---

## Step 6 — Frontend: field type registry

**`frontend/src/config/fieldTypes.ts`**
- Import the new component at the top alongside the other field imports.
- Add an entry to `FIELD_TYPE_DEFINITIONS`:
  ```ts
  {
    name: Fieldtype.<SCREAMING_SNAKE>,
    component: <ComponentName>,
    props: {},           // default props forwarded to the component
    layout: "default",   // or "inline" / "description-first" / "custom"
    frappeFieldtype: "<FrappeFieldtype>",
    isBoolean: false,    // true only for Switch / Checkbox analogues
    isDate: false,       // true only for Date / DateTime / DateRange / Time analogues
  },
  ```

  Layout guide:
  - `"default"` — label top, input below, description at bottom (most fields)
  - `"inline"` — input first, label to the right (Switch, Checkbox)
  - `"description-first"` — label, description, then input (Text Editor)
  - `"custom"` — component owns its full layout (Table, Attach)

---

## Step 7 — Frontend: options resolution

**`frontend/src/utils/selectOptions.ts`** — `getFieldOptions`

If the new field type uses newline-separated options (like Select / Multiselect), add `"<FieldtypeName>"` to the existing condition:
```ts
if (field.fieldtype === "Select" || field.fieldtype === "Multiselect" || field.fieldtype === "<FieldtypeName>") {
  return field.options.split("\n");
}
```
If it uses a Link-style async lookup or no options at all, adjust or skip accordingly.

---

## Step 8 — Frontend: submission display

**`frontend/src/components/form/submissions/SubmissionFieldValue.vue`**

Add a display case before the generic `v-else` fallback. Examples:

- For a JSON array field:
  ```ts
  const parsed<Name>Value = computed(() => {
    if (!props.value) return "–";
    try {
      const parsed = JSON.parse(props.value);
      if (Array.isArray(parsed)) return parsed.join(", ");
    } catch { /* already a string */ }
    return String(props.value);
  });
  ```
  ```vue
  <span v-else-if="fieldtype === Fieldtype.<SCREAMING_SNAKE>" class="text-sm text-ink-gray-7">
    {{ parsed<Name>Value }}
  </span>
  ```

- For a simple scalar, the generic `v-else` fallback already handles it — no change needed.

---

## Step 9 — Typecheck

Run:
```bash
cd frontend && yarn typecheck
```

Fix any TypeScript errors before committing. Common issues:
- Forgot to add the enum member to `Fieldtype`
- `FIELD_TYPE_DEFINITIONS` exhaustiveness error — TypeScript will point to the missing entry

---

## Step 10 — Commit

Create three commits (no co-author line):

1. `feat(form-field): add <FieldtypeName> fieldtype to doctype and backend mapping`
   - `form_field.json`, `form_field.py`

2. `fix(submission): <any submission serialization changes>` *(skip if no changes needed)*

3. `feat(<fieldtype-kebab>): wire up <FieldtypeName> field across the frontend`
   - `form_field.types.ts`, `fieldTypes.ts`, `<FieldtypeName>.vue`, `selectOptions.ts`, `SubmissionFieldValue.vue`
