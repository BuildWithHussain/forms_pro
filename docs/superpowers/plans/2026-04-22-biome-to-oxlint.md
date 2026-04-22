# Biome to oxlint Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Biome with oxlint for linting. Keep Prettier for formatting (already in pre-commit).

**Why oxlint:** 50-100x faster than ESLint, Rust-based, better ESLint rule compatibility than Biome.

**Current state:**
- `@biomejs/biome` in devDependencies
- `biome.json` config with recommended rules, tab indent, double quotes
- `yarn lint` runs `biome check --write .`
- Pre-commit has ESLint (no config) + Prettier

**Target state:**
- `oxlint` in devDependencies
- `oxlint.json` config
- `yarn lint` runs `oxlint`
- Pre-commit uses oxlint + Prettier

---

## File Map

| File | Change |
|---|---|
| `frontend/package.json` | Remove `@biomejs/biome`, add `oxlint`; update `lint` script |
| `frontend/biome.json` | **Delete** |
| `frontend/oxlint.json` | **Create** |
| `.pre-commit-config.yaml` | Replace ESLint hook with oxlint |

---

## Task 1: Install oxlint, remove Biome

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Remove Biome, add oxlint**

```bash
cd frontend && yarn remove @biomejs/biome && yarn add -D oxlint
```

- [ ] **Step 2: Update lint script in package.json**

Change:
```json
"lint": "biome check --write .",
```

To:
```json
"lint": "oxlint .",
```

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/yarn.lock
git commit -m "chore(deps): replace @biomejs/biome with oxlint"
```

---

## Task 2: Create oxlint config

**Files:**
- Create: `frontend/oxlint.json`
- Delete: `frontend/biome.json`

- [ ] **Step 1: Create `frontend/oxlint.json`**

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "warn",
    "eqeqeq": "error"
  },
  "ignorePatterns": [
    "dist/**",
    "coverage/**",
    "node_modules/**"
  ]
}
```

- [ ] **Step 2: Delete biome.json**

```bash
rm frontend/biome.json
```

- [ ] **Step 3: Commit**

```bash
git add frontend/oxlint.json
git add frontend/biome.json  # staged as deleted
git commit -m "chore: add oxlint config, remove biome.json"
```

---

## Task 3: Update pre-commit config

**Files:**
- Modify: `.pre-commit-config.yaml`

- [ ] **Step 1: Replace ESLint hook with oxlint**

Find and remove:
```yaml
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        types_or: [javascript, ts]
        args: ["--quiet"]
        # Ignore any files that might contain jinja / bundles
```

Replace with:
```yaml
  - repo: https://github.com/oxc-project/oxlint
    rev: v0.16.6
    hooks:
      - id: oxlint
        types_or: [javascript, ts, vue]
```

- [ ] **Step 2: Install pre-commit hooks**

```bash
pre-commit install
```

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore(pre-commit): replace eslint with oxlint"
```

---

## Task 4: Verify and fix lint errors

- [ ] **Step 1: Run oxlint and fix any errors**

```bash
cd frontend && yarn lint
```

Fix any reported issues.

- [ ] **Step 2: Run pre-commit on all files**

```bash
pre-commit run --all-files
```

- [ ] **Step 3: Commit fixes if any**

```bash
git add -A
git commit -m "fix: resolve oxlint findings"
```

---

## Task 5: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update lint command reference**

Find:
```markdown
# Lint & format (BiomeJS)
cd frontend && yarn lint
```

Replace with:
```markdown
# Lint (oxlint) & format (Prettier via pre-commit)
cd frontend && yarn lint
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for oxlint"
```
