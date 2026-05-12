---
name: writing-tests
description: Use when writing or modifying backend tests in `forms_pro/tests/`. Forms Pro test suites must build test documents via `frappe_factory_bot` factories rather than `frappe.new_doc` / `frappe.get_doc`. This skill explains where factories live, how to author one, and how to consume them in tests.
---

# Writing Tests (frappe_factory_bot)

The dev bench has `frappe_factory_bot` installed alongside Forms Pro (`apps/frappe_factory_bot`, repo: `harshtandiya/frappe_factory_bot`). All Forms Pro tests build their fixtures through factories defined in `forms_pro/tests/factories/`.

## Rules

1. **Never** call `frappe.new_doc(...)` or `frappe.get_doc({...}).insert()` directly in a test to spin up a fixture. Use a factory.
2. One factory per doctype. File name: `<snake_case_doctype>_factory.py` inside `forms_pro/tests/factories/`.
3. Factory class name: `<PascalCaseDocType>Factory`, subclassing `BaseFactory[<DocClass>]` (parameterise the generic with the actual `Document` subclass for type hints).
4. `default_attributes` must only set the minimum fields required for `.insert()` to succeed. Use `Faker` (`_fake = Faker()`) with `_fake.unique.*` when a field must be unique.
5. Reuse the factory bot's primitives instead of reinventing them:
   - **Traits**: extra `@property` methods returning attribute dicts. Apply with `Factory.create("trait_name")`.
   - **Overrides**: kwargs to `create()` / `build()`. Take precedence over traits and defaults.
   - **Relationships**: in a trait that fabricates a related doc, *always* honour `self.overrides.get("<fk_field>")` before creating a new dependent record (prevents orphans).
6. Factory bot owns teardown via `__del__` hooks. Do **not** add manual cleanup of factory-built docs in tearDown.
7. If a doctype you need has no factory yet, write one first, then write the test. Keep the factory commit / change separate-ish from test logic when reasonable.

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
        return {
            "title": _fake.unique.sentence(nb_words=3),
            "is_active": 1,
        }

    @property
    def with_owner_team(self) -> dict[str, Any]:
        # Honour the override so callers can pass an existing team.
        from forms_pro.tests.factories.fp_team_factory import FPTeamFactory

        return {
            "owner_team": self.overrides.get("owner_team") or FPTeamFactory.create().name,
        }
```

Reference existing factories:
- `forms_pro/tests/factories/user_factory.py` — typed generic (`BaseFactory[User]`), `Faker.unique`, `with_forms_pro_role` trait that seeds a child table.
- `forms_pro/tests/factories/fp_team_factory.py` — minimal default attributes.
- `forms_pro/tests/factories/user_invitation_factory.py` — overrides-aware defaults + `to_forms_pro_app` trait.

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

if you want to run a specific test, you can use the following command:

```bash
bench --site forms.dev run-tests --module *path_to_test_file* --test *test_method_name* 
```