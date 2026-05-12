---
name: writing-tests
description: Use when writing or modifying backend tests in `forms_pro/tests/`. Forms Pro test suites must build test documents via `frappe_factory_bot` factories rather than `frappe.new_doc` / `frappe.get_doc`. This skill explains where factories live, how to author one, and how to consume them in tests.
---

# Writing Tests (frappe_factory_bot)

The dev bench has `frappe_factory_bot` installed alongside Forms Pro (`apps/frappe_factory_bot`, repo: `harshtandiya/frappe_factory_bot`). All Forms Pro tests build their fixtures through factories defined in `forms_pro/tests/factories/`.

## Rules

1. **Never** call `frappe.new_doc(...)` or `frappe.get_doc({...}).insert()` directly in a test to spin up a fixture. Use a factory.
2. One factory per doctype. File name: `<snake_case_doctype>_factory.py` inside `forms_pro/tests/factories/`. **Naming exception**: when a doctype is used in a narrow domain context (e.g. the generic `"DocType"` doctype acting as a placeholder for a Form's linked DocType), name the factory after the domain — `LinkedFormDoctypeFactory`, not `DoctypeFactory`.
3. Factory class name: `<PascalCaseDocType>Factory`, subclassing `BaseFactory[<DocClass>]` (parameterise the generic with the actual `Document` subclass for type hints).
4. `default_attributes` must only set the minimum fields required for `.insert()` to succeed. Use `Faker` (`_fake = Faker()`) with `_fake.unique.*` when a field must be unique.
5. Reuse the factory bot's primitives instead of reinventing them:
   - **Traits**: extra `@property` methods returning attribute dicts. Apply with `Factory.create("trait_name")`.
   - **Overrides**: kwargs to `create()` / `build()`. Take precedence over traits and defaults.
   - **Relationships (in traits)**: in a trait that fabricates a related doc, *always* honour `self.overrides.get("<fk_field>")` before creating a new dependent record (prevents orphans).
   - **Relationships (in defaults)**: when a required FK has no sensible literal default, use the same `self.overrides.get(...) or RelatedFactory.create().name` short-circuit inside `default_attributes` so callers can pass an existing record without spawning an orphan.
6. Factory bot owns teardown via `__del__` hooks. Do **not** add manual cleanup of factory-built docs in tearDown.
7. **Do not override `create()`** to wrap heavy side effects. If a doctype needs more than `frappe.get_doc({...}).insert()` to be usable (parent DocType, DocShare, etc.), build a separate factory for the dependency and reference it from `default_attributes` (see rule 5). Overriding `create()` breaks `build_list` / `create_list` and diverges from the convention.
8. If a doctype you need has no factory yet, write one first, then write the test. Keep the factory commit / change separate-ish from test logic when reasonable.

## Authoring a factory

Template — replace placeholders. Note the generic `BaseFactory[FooBar]` typing.

```python
from typing import Any

from faker import Faker
from frappe_factory_bot.frappe_factory_bot.base_factory import BaseFactory

from forms_pro.forms_pro.doctype.foo_bar.foo_bar import FooBar

_fake = Faker()


class FooBarFactory(BaseFactory[FooBar]):
    doctype = "Foo Bar"

    @property
    def default_attributes(self) -> dict[str, Any]:
        from forms_pro.tests.factories.fp_team_factory import FPTeamFactory

        return {
            "title": _fake.unique.sentence(nb_words=3),
            "is_active": 1,
            # Lazy-create the FK only if the caller did not pass one.
            "owner_team": self.overrides.get("owner_team") or FPTeamFactory.create().name,
        }

    @property
    def with_owner_team(self) -> dict[str, Any]:
        # Same honour-override pattern, applicable to optional FKs surfaced via traits.
        from forms_pro.tests.factories.fp_team_factory import FPTeamFactory

        return {
            "owner_team": self.overrides.get("owner_team") or FPTeamFactory.create().name,
        }
```

Reference existing factories:
- `forms_pro/tests/factories/user_factory.py` — `Faker.unique`, `with_forms_pro_role` trait that seeds a child table.
- `forms_pro/tests/factories/fp_team_factory.py` — minimal default attributes.
- `forms_pro/tests/factories/user_invitation_factory.py` — overrides-aware defaults + `to_forms_pro_app` trait.
- `forms_pro/tests/factories/form_factory.py` + `linked_form_doctype_factory.py` — pattern for a doctype with non-trivial dependencies; defaults lazy-create the placeholder DocType and team.

## Gotchas

### `__del_override__` fires on garbage collection

`BaseFactory._attach_del` swaps the returned doc's class so its `__del__` runs cleanup. Python invokes `__del__` when the doc is GC'd. If you chain `Factory.create().name` and discard the doc, the cleanup may run **before** the FK is used downstream, deleting the doc you just relied on.

```python
# Risky — DocType may be GC'd before the Form insert reads its name.
fk = MyDocTypeFactory.create().name

# Safe — binding keeps the doc alive for the test's lifetime.
parent = MyDocTypeFactory.create()
fk = parent.name
```

For factories that do not need destructive cleanup (e.g. DocTypes whose unique random names provide isolation), it is acceptable to skip the `__del_override__` override entirely.

### `before_insert` / `validate` can clobber overrides

Some doctypes hard-set fields during `before_insert` (e.g. `Form.before_insert` forces `is_published = False`). Passing `is_published=1` as a factory override is silently overwritten — the override is merged into the dict that becomes the new doc, but `before_insert` runs after that and overwrites the attribute.

Patch post-insert when this matters:

```python
form = FormFactory.create(...)
form.is_published = 1
form.save(ignore_permissions=True)
```

Rule of thumb: if the doctype hard-sets a field in `before_insert`, `validate`, or `before_validate`, factory overrides cannot reach it — touch the field after `.create()` and save again.

## Consuming factories in tests

```python
import frappe
from frappe.tests import IntegrationTestCase

from forms_pro.tests.factories.user_factory import UserFactory
from forms_pro.tests.factories.fp_team_factory import FPTeamFactory


class TestSomething(IntegrationTestCase):
    def test_invites_existing_member(self) -> None:
        user = UserFactory.create("with_forms_pro_role")
        team = FPTeamFactory.create(owner=user.name)
        # IDE knows `user: User` and `team: FPTeam` thanks to BaseFactory[T].
        frappe.set_user(user.name)
        ...
```

Method cheat sheet (all class methods on the factory):

| Call | Returns | Saved? |
| --- | --- | --- |
| `Factory.build(*traits, **overrides)` | `T` | no |
| `Factory.create(*traits, **overrides)` | `T` | yes |
| `Factory.build_list(n, *traits, **overrides)` | `list[T]` | no |
| `Factory.create_list(n, *traits, **overrides)` | `list[T]` | yes |

Precedence: overrides > traits > defaults. Passing a trait that does not exist raises `TypeError`.

## Test runner

```bash
bench --site forms.dev run-tests --module forms_pro.tests.test_<module>
```

The command above will run tests inside the module.

If you want to run all tests, you can use the following command:

```bash
bench --site forms.dev run-tests --app forms_pro
```

If you want to run a specific test, you can use the following command:

```bash
bench --site forms.dev run-tests --module *path_to_test_file* --test *test_method_name*
```
