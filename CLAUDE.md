# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Forms Pro is a Frappe app that lets users build forms linked to any Frappe DocType. It has two main parts:
- **Backend**: Frappe app (`forms_pro/`) — Python, doctypes, API endpoints, hooks
- **Frontend**: Vue 3 SPA (`frontend/src/`) — served at `/forms/`, built to `forms_pro/public/frontend/`

## Commands

### Frontend
```bash
# Development (Vite dev server on port 8080)
npm run dev

# Production build (outputs to forms_pro/public/frontend/)
npm run build

# TypeScript type check
cd frontend && yarn typecheck

# Lint & format (BiomeJS)
cd frontend && yarn lint
```

### Backend Tests
```bash
# Run all app tests
bench --site <site> run-tests --app forms_pro

# Run a specific test module
bench run-tests --module forms_pro.tests.test_roles
```

### Pre-commit
```bash
pre-commit run --all-files
```
Pre-commit runs `ruff` (Python), `prettier` (Vue/TS/SCSS), and `eslint` (JS/TS).

## Architecture

### Backend

**API Layer** (`forms_pro/api/`): Whitelisted Frappe methods callable from the frontend.
- `form.py` — form CRUD, sharing, doctype field introspection
- `submission.py` — submit responses, retrieve user submissions
- `team.py` — team creation, member management, invitations
- `user.py` — current user, user teams

**Doctypes** (`forms_pro/forms_pro/doctype/`):
- `Form` — main form entity; links to any Frappe DocType; has `FormField` child table; tracks sharing, publication, success message
- `FormField` — a field in a form; maps to a DocType field; stores conditional logic
- `FPTeam` / `FPTeamMember` — team and membership; `FPTeam.users` is a `TableMultiSelect` of `FPTeamMember`
- `FPTeamInvitation` — pending team invitations

**Form Submission Flow**:
1. `api/submission.py:submit_form_response()` receives field values
2. Creates a new document in the linked DocType
3. Auto-injects `fp_linked_form` and `fp_submission_status` custom fields (created by `utils/form_generator.py` when the form is saved)
4. Shares the new document with the submitter

**Form-DocType Sync** (`Form.set_doctype_fields()`):
When a form is saved, its fields are synced to the linked DocType as `CustomField` records. Renaming a form field updates the underlying DocType field.

**Hooks** (`hooks.py`):
- `user_invitation.after_accept` → `overrides/invitations.py` — adds invited user to their team server-side
- `doc_events["User"].on_update` → `overrides/roles.py` — creates a default team for new Forms Pro users
- Website route rule: `/forms/<path:app_path>` → `www/forms.py` (serves the SPA)

**Permissions**: Form-level access uses Frappe's `DocShare`. Team membership is stored in `FPTeamMember`. Always check `team.is_team_member(email)` before calling `team.add_to_team(email)` — the latter throws `DuplicateEntryError` if already a member.

### Frontend

**Routing** (`src/router.ts`, base `/forms`):
| Path | Page | Notes |
|---|---|---|
| `/` | Dashboard | Lists user's forms |
| `/team` | ManageTeam | Team settings/members |
| `/manage/:id` | ManageForm | Form overview + submissions |
| `/edit-form/:id` | EditForm | Drag-and-drop form builder |
| `/p/:route(...)` | SubmissionPage | Public form (allow_guest) |
| `/p/:route(...)/edit/:submissionName` | PublicEdit | Edit existing submission |

**State** (`src/stores/`): Pinia stores.
- `user.ts` — current user, teams list, active team, theme
- `editForm.ts` — form-builder state: selected field, doctype fields available
- `submissionForm.ts` — live field values during submission
- `editSubmission.ts` — values when editing an existing submission

**Component Layout**:
- `src/components/builder/` — form builder canvas and field editors
- `src/components/fields/` — per-field-type renderers (Data, Email, Select, Date, etc.)
- `src/components/form/` — form rendering (used in submission page)
- `src/components/ui/` — generic UI primitives
- `src/data/` — Frappe resource wrappers (`session.ts`, `user.ts`)
- `src/utils/conditionals.ts` — evaluates conditional-show logic at runtime

**API Calls**: Use `frappe.call()` (via frappe-ui) pointing to the whitelisted Python methods in `forms_pro/api/`. Guest-accessible endpoints use `allow_guest=True` in the Python decorator.

## Skills

| Skill | Description |
|---|---|
| `/release [version]` | Draft a new GitHub release. Inspects merged PRs since the last release, categorizes them, and creates a draft on GitHub for review. |
| `/add-field <FieldtypeName>` | Add a new field type end-to-end: backend doctype + mapping, submission serialization, frontend component, fieldTypes registry, options resolution, and submission display. |

## Key Conventions

- **Python target**: 3.14+; formatted with `ruff`
- **TypeScript**: strict mode; `vue-tsc` enforced in CI
- **Frappe patterns**: use `frappe.get_doc`, `frappe.get_all`, `frappe.db.*`; avoid raw SQL unless necessary
- **PR titles**: validated by CI workflow (conventional commit format expected)
- **Tests**: use Frappe's `IntegrationTestCase`; test infrastructure set up in `install.py:before_tests()`
