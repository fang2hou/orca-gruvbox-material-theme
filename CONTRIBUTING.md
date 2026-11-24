# Contributing

This document covers how changes land.
Development setup lives in [DEVELOPMENT.md](./DEVELOPMENT.md); rules for AI agents live in [AGENTS.md](./AGENTS.md).

## Ground Rules

- Smallest complete change that solves the requirement.
- No unrelated cleanup mixed into color or mapping changes.
- No new dependencies without justification (see the guidelines' dependency discipline).

## Reporting a Bug

- Search existing issues first.
- Name the theme (for example `Gruvbox Material Light (Soft, Mix)`), the Orca version, and what looks wrong; a screenshot helps.

## Proposing a Change

Open an issue before changing a role mapping or a theme name, because installed users see the result immediately.

## Pull Request Workflow

1. Branch from `main`.
2. Implement; keep `mise run test` green and commit regenerated files with the change.
3. Commit messages follow Conventional Commits (validated by Cocogitto).
4. Open a PR; CI must pass.
5. Squash merge (the only allowed method).

## Review Expectations

Reviewers check:

- The colors match the request, in Orca and in `mise run report`.
- Generated files come from `mise run generate`, not hand edits.
- No accidental scope creep, files, or dependencies.
- Compatibility with the invariants in [ARCHITECTURE.md](./ARCHITECTURE.md).
- No sensitive information.

## Commit Conventions

Conventional Commits, enforced by Cocogitto locally and in CI:

```text
feat(themes): add bold to type names
fix(contrast): keep chat diff text readable on Light Soft
```

With squash merging, the PR title must follow the same convention (it becomes the commit message).

## Pull Request Descriptions

Every pull request description must clearly include:

- **Purpose**: what the change is for
- **Impact**: which themes, tokens or tooling are affected
- **Context**: relevant background
- **Risks**: potential concerns
- **Testing**: validation performed and its results

The GitHub pull request template asks for the same five items.
