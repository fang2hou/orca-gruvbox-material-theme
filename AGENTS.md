# AGENTS.md

Guidance for AI agents working in this repository. Read this before making changes.

An Orca plugin that ships every Gruvbox Material variant as app, syntax and terminal themes, plus the Python generator that produces them.

## Commands

```bash
mise install                 # set up the toolchain (Python, uv, ruff, prek, cog, gitleaks)
mise run generate            # regenerate themes/, terminal/ and orca-plugin.json contributes
mise run report              # list contrast-driven color adjustments per variant
mise run format              # ruff format + ruff check --fix
mise run check               # lint, format check, secret scan, generated files current and Orca-safe
mise run test                # check, then unit tests
uv run --locked python -m unittest tests.test_themes   # one test module
mise run cover               # re-render images/cover.png (Playwright, fetched on first run)
mise run validate-plugin     # orca plugin validate . (needs Orca installed; not in CI)
```

Use `uv run`, never bare `python` or `pip`.

## Engineering Standards

This project follows the shared engineering guidelines:

> https://github.com/fang2hou/ai-coding-guidelines/blob/main/PORTAL.md

Read the portal's reading recipes for your task type before starting.
Repository documentation always takes precedence over remembered summaries.

Project-specific overrides:

- Ruff `line-length = 120`: palette rows and scope lists are data that reads worse wrapped.
- The package lives in `src/gruvbox_orca/` but is never published; the plugin version is `version` in `orca-plugin.json`.

## Layout

- `src/gruvbox_orca/`: `palette.py` (upstream colors), `themes.py` (role mapping), `orca_check.py` (port of Orca's contrast check), `build.py` (CLI), `cover.py` + `cover.css` (cover image).
- `tests/`: unit tests for the contrast check and the generator.
- `themes/`, `terminal/`: generated plugin content.
- `images/`: the plugin cover.

## Boundaries

Always:

- Run `mise run test` before every commit.
- Run `mise run generate` and `mise run cover` after changing colors or mappings, and commit the results together.
- Run `mise run validate-plugin` after changing `orca-plugin.json`.

Never:

- Hand-edit `themes/*.json`, `terminal/*.json` or the `contributes` section of `orca-plugin.json`; change `src/gruvbox_orca/` and run `mise run generate`.
- Change a palette value in `palette.py` unless upstream changed it.
- Weaken a floor in `orca_check.py`; it must match Orca's renderer.

Ask first:

- Adding a dependency.
- Changing the plugin `id`, a theme `id`, or a theme title (installed users lose their selection).
- Changing a role mapping in `themes.py` that alters colors users already see.

## Confirmed Language Policy

| Item                      | Value                                   |
| ------------------------- | --------------------------------------- |
| Conversation              | Follows the user                        |
| Code / comments / commits | English                                 |
| UI language               | English (theme titles and manifest text) |
| Tone                      | Plain, factual                          |

Do not infer UI language from conversation language.

## Project Conventions

- A color only moves when a contrast rule fails, by the smallest 1% step toward `fg0`; `mise run report` shows every move.
- `orca_check.py` mirrors Orca's renderer, including that a failing pair drops both tokens. When Orca changes its check, update the port and its tests together.
- Orca's editor maps every plain identifier to the `variable` scope, so `variable` stays `fg0`.
- The repository root is the plugin folder. Keep symlinks and large trees out of it: run Python through mise so uv uses `UV_PROJECT_ENVIRONMENT` outside the repo, and check with `orca plugin inspect .`.

Depth: [DEVELOPMENT.md](./DEVELOPMENT.md) for workflow and toolchain, [CONTRIBUTING.md](./CONTRIBUTING.md) for PR rules, [ARCHITECTURE.md](./ARCHITECTURE.md) for invariants and the palette mapping.
