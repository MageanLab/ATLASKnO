# ATLASKnO — CI/CD Setup Guide

Step-by-step instructions for configuring the GitHub Actions CI/CD pipeline,
PyPI trusted publishing, branch protection, and local developer tooling.

---

## Table of Contents

1. [Repository Secrets](#1-repository-secrets)
2. [GitHub Environments](#2-github-environments)
3. [PyPI Trusted Publisher (OIDC)](#3-pypi-trusted-publisher-oidc)
4. [Branch Protection Rules](#4-branch-protection-rules)
5. [Local Pre-commit Setup](#5-local-pre-commit-setup)
6. [Conventional Commits](#6-conventional-commits)
7. [First Release Checklist](#7-first-release-checklist)

---

## 1. Repository Secrets

The pipeline is designed to **minimize required secrets**. Most authentication
uses GitHub's built-in `GITHUB_TOKEN` or OIDC tokens.

| Secret | Required? | Purpose |
|--------|-----------|---------|
| `GITHUB_TOKEN` | ✅ Auto-provided | GitHub Release creation, Gitleaks scanning |
| `PYPI_API_TOKEN` | ❌ Not needed | Replaced by OIDC Trusted Publishing (see §3) |

### Optional Secrets (for extended workflows)

If you add integrations later, you may need:

| Secret | When needed |
|--------|-------------|
| `CODECOV_TOKEN` | If you add Codecov coverage reporting |
| `SLACK_WEBHOOK_URL` | If you add Slack notifications |
| `DOCKER_HUB_TOKEN` | If you add container publishing |

**To add a secret:**
1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Enter the name and value

---

## 2. GitHub Environments

The release workflow uses a `pypi` environment for deployment protection.

### Create the `pypi` environment:

1. Go to **Settings → Environments → New environment**
2. Name it: `pypi`
3. Configure protection rules:
   - ✅ **Required reviewers**: Add 1-2 maintainers who must approve releases
   - ✅ **Wait timer**: Optional, e.g., 5 minutes delay before deployment
   - **Deployment branches**: Restrict to `main` branch only

---

## 3. PyPI Trusted Publisher (OIDC)

This pipeline uses **PyPI Trusted Publishing** — no API tokens are stored as
secrets. Instead, GitHub and PyPI establish trust via OIDC.

### Initial Setup (one-time):

#### If the package does NOT exist on PyPI yet:

1. Go to [pypi.org/manage/account/publishing](https://pypi.org/manage/account/publishing/)
2. Under **"Add a new pending publisher"**, fill in:
   - **PyPI Project Name**: `atlaskno`
   - **Owner**: `MageanLab`
   - **Repository name**: `ATLASKnO`
   - **Workflow name**: `release-publish.yml`
   - **Environment name**: `pypi`
3. Click **"Add"**

#### If the package already exists on PyPI:

1. Go to [pypi.org/manage/project/atlaskno/settings/publishing/](https://pypi.org/manage/project/atlaskno/settings/publishing/)
2. Under **"Add a new publisher"**, fill in the same values as above
3. Click **"Add"**

### How it works:

```
GitHub Actions → OIDC Token → PyPI verifies:
  ├── Repository = MageanLab/ATLASKnO  ✓
  ├── Workflow   = release-publish.yml  ✓
  ├── Environment = pypi                ✓
  └── Publishes package                 🚀
```

> **Note:** No `PYPI_API_TOKEN` secret is needed. The `pypa/gh-action-pypi-publish`
> action automatically handles OIDC authentication.

---

## 4. Branch Protection Rules

Configure these for all three long-lived branches:

### `main` (Production)

1. Go to **Settings → Branches → Add branch ruleset** (or classic protection rule)
2. Branch name pattern: `main`
3. Enable:
   - ✅ **Require a pull request before merging**
     - Required approvals: **2**
     - Dismiss stale reviews: ✅
     - Require review from code owners: ✅
   - ✅ **Require status checks to pass before merging**
     - Required checks:
       - `Lint & Format (Ruff + Mypy)`
       - `Security Scan`
       - `Unit Tests (Python 3.12)`
       - `License Compliance`
   - ✅ **Require conversation resolution before merging**
   - ✅ **Require signed commits** (recommended)
   - ✅ **Require linear history** (recommended for clean changelogs)
   - ✅ **Do not allow bypassing the above settings**
   - ❌ **Do not allow force pushes**
   - ❌ **Do not allow deletions**

### `staging` (Pre-release QA)

Same as `main` except:
- Required approvals: **1**
- Additional required checks:
  - `Integration Tests`
  - `Build & Package Dry-Run`
  - `Documentation Build`

### `develop` (Integration)

Lighter protection:
- ✅ **Require a pull request before merging**
  - Required approvals: **1**
- ✅ **Require status checks to pass**
  - Required checks:
    - `Lint & Format (Ruff + Mypy)`
    - `Unit Tests (Python 3.12)`
- ❌ Signed commits not required (developer convenience)

---

## 5. Local Pre-commit Setup

### Installation:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks (run from repo root)
pre-commit install
pre-commit install --hook-type commit-msg   # For conventional commits

# Run against all files (first-time or CI)
pre-commit run --all-files
```

### What it enforces locally:

| Hook | What it does |
|------|--------------|
| `trailing-whitespace` | Removes trailing whitespace |
| `end-of-file-fixer` | Ensures files end with a newline |
| `check-yaml` | Validates YAML syntax |
| `check-toml` | Validates TOML syntax |
| `check-json` | Validates JSON syntax |
| `detect-private-key` | Blocks accidental key commits |
| `ruff` | Lints Python (auto-fix mode) |
| `ruff-format` | Formats Python code |
| `mypy` | Type-checks Python |
| `bandit` | Security scans Python |
| `gitleaks` | Scans for leaked secrets |
| `commitizen` | Enforces conventional commit format |

### Skipping hooks (emergency):

```bash
# Skip all hooks for a single commit
git commit --no-verify -m "hotfix: emergency patch"

# Skip specific hooks
SKIP=mypy git commit -m "feat: work in progress"
```

---

## 6. Conventional Commits

The changelog generator (`git-cliff`) requires conventional commit messages.

### Format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Common types:

| Type | Usage | Changelog group |
|------|-------|-----------------|
| `feat` | New feature | 🚀 Features |
| `fix` | Bug fix | 🐛 Bug Fixes |
| `docs` | Documentation change | 📚 Documentation |
| `data` | Data/schema changes | 📊 Data & Schemas |
| `refactor` | Code refactoring | 🔧 Refactoring |
| `test` | Adding/updating tests | 🧪 Testing |
| `ci` | CI/CD changes | ⚙️ CI/CD |
| `perf` | Performance improvement | ⚡ Performance |
| `chore` | Maintenance | 📦 Miscellaneous |

### Examples:

```bash
feat(parser): add JSON-LD export support
fix(taxonomy): resolve cycle in class 5xx hierarchy
data(schedules): update UDC Main Tables to 2026 edition
docs: add API reference for CLI tools
ci: add SHACL validation to semantic pipeline
```

### Breaking changes:

```bash
feat(api)!: change response format to JSON-LD
# or
feat(api): change response format

BREAKING CHANGE: API responses now return JSON-LD instead of plain JSON.
```

---

## 7. First Release Checklist

When you're ready to cut the first release:

- [ ] Ensure `pyproject.toml` has the correct version (`0.1.0`)
- [ ] Set up PyPI Trusted Publisher (§3)
- [ ] Create the `pypi` GitHub Environment (§2)
- [ ] Configure branch protection (§4)
- [ ] Install pre-commit locally (§5)
- [ ] Create your first conventional commit
- [ ] Merge to `develop` → `staging` → `main`
- [ ] Tag and push:
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```
- [ ] Watch the release pipeline execute 🚀

---

## Workflow Architecture Diagram

```
feature/* ──PR──► develop ──PR──► staging ──PR──► main ──tag──► Release
    │                │                │               │
    ▼                ▼                ▼               ▼
 PR Quality     PR Quality      Staging QA      Release & Publish
  Gate            Gate          ┌───────────┐   ┌──────────────────┐
 ┌──────────┐  ┌──────────┐   │Integration │   │ Changelog        │
 │ Lint     │  │ Lint     │   │ Tests      │   │ GitHub Release   │
 │ Security │  │ Security │   │ Build      │   │ PyPI Publish     │
 │ Tests    │  │ Tests    │   │ Dry-Run    │   │ SLSA Attestation │
 │ License  │  │ License  │   │ Docs Build │   └──────────────────┘
 └──────────┘  └──────────┘   └───────────┘

        Semantic Validation (path-filtered on data changes)
        ┌──────────────────────────────────────────────┐
        │ RDF Syntax │ Taxonomy Integrity │ SHACL       │
        └──────────────────────────────────────────────┘
```
