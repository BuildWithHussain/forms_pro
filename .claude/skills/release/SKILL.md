---
name: release
description: Draft a new GitHub release for buildwithhussain/forms_pro by inspecting existing releases and merged PRs since the last release. Use when the user wants to cut, draft, or create a release.
argument-hint: [version]
---

You are preparing a new GitHub release for the repo `buildwithhussain/forms_pro`.

## Steps

1. **Fetch current releases**
   Run: `gh release list --repo buildwithhussain/forms_pro`

2. **Inspect the latest release** to get its tag and published date:
   Run: `gh release view <latest-tag> --repo buildwithhussain/forms_pro`

3. **List all merged PRs** since the last release (sorted by merge date):
   Run: `gh pr list --repo buildwithhussain/forms_pro --state merged --limit 100 --json number,title,author,mergedAt | jq 'sort_by(.mergedAt)'`
   Filter to only PRs merged **after** the last release's published date.

4. **Determine the next version**
   - If `$ARGUMENTS` is provided, use it as the tag (e.g. `v0.1.3-beta`).
   - Otherwise, infer the next patch version from the latest tag (e.g. `v0.1.1-beta` → `v0.1.2-beta`).

5. **Categorize PRs** into:
   - **Features** — titles starting with `feat:`
   - **Fixes** — titles starting with `fix:`
   - **Chores / CI** — titles starting with `chore:`, `refactor:`, `ci:`, `docs:` — **omit these from release notes**

6. **Show the user a plan**: list the proposed tag, target branch (`main`), and the drafted release notes. Ask for confirmation before creating anything.

7. **After confirmation**, create a draft release:
   ```
   gh release create <tag> \
     --repo buildwithhussain/forms_pro \
     --title "<tag>" \
     --draft \
     --target main \
     --notes "<release notes>"
   ```

8. Return the draft release URL so the user can review and publish it.

## Release Notes Format

Follow the same format as previous releases exactly:

```markdown
## What's Changed

### Features
* feat: <title> by @<author> in https://github.com/BuildWithHussain/forms_pro/pull/<number>

### Fixes
* fix: <title> by @<author> in https://github.com/BuildWithHussain/forms_pro/pull/<number>

**Full Changelog**: https://github.com/BuildWithHussain/forms_pro/compare/<previous-tag>...<new-tag>
```

Omit a section entirely if there are no PRs in that category.
