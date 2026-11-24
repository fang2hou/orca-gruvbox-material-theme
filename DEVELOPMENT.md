# Development

How development is performed in this repository, for both humans and AI agents.
User-facing setup lives in the README; this document is for people changing the themes or the generator.

## Setup

All tools are managed by mise.

```bash
mise install
uv sync
prek install
```

| Tool      | Purpose                                    | Managed via      |
| --------- | ------------------------------------------ | ---------------- |
| Python    | Generator runtime (3.12)                   | `mise.toml`      |
| uv        | Environment and dependencies               | `mise.toml`      |
| ruff      | Linter and formatter                       | `mise.toml`      |
| prek      | Git hooks (`mise run check`, commit message) | `mise.toml`    |
| cocogitto | Conventional Commits validation            | `mise.toml`      |
| gitleaks  | Secret scanning                            | `mise.toml`      |
| Playwright | Cover rendering only (`cover` group)      | `pyproject.toml` |

`UV_PYTHON_PREFERENCE=only-system` in `mise.toml` makes uv use mise's pinned Python instead of downloading its own.
`UV_PROJECT_ENVIRONMENT` keeps the virtual environment in `~/.cache/uv-projects/` because the repository root is the plugin folder: Orca refuses plugin folders that contain symlinks (a `.venv` has them) or more than 2,000 entries.
Do not substitute tools without explicit approval (see the guidelines repository's toolchain standards).

## Commands

```bash
mise run generate         # write themes/, terminal/ and the manifest's contributes section
mise run report           # show which colors each variant nudged, and why
mise run check            # lint, format check, secret scan, generated files current and Orca-safe (what CI runs)
mise run test             # check, then unit tests
mise run format           # apply ruff formatting and fixes
mise run cover            # re-render images/cover.png
mise run validate-plugin  # orca plugin validate . (local only, needs Orca)
```

`mise run` lists every task.

## Workflow

1. Branch from `main`.
2. Change `src/gruvbox_orca/` (never the generated JSON).
3. `mise run generate`, then `mise run report` to see what moved.
4. `mise run cover` when colors changed; look at the image.
5. `mise run test` and `mise run validate-plugin` must pass.
6. Check the result in Orca: `orca plugin dev load .`, switch to the affected themes, then `orca plugin dev unload .`.
7. Commit with Conventional Commits (validated by Cocogitto) and open a PR following [CONTRIBUTING.md](./CONTRIBUTING.md).

## Layout

- `src/gruvbox_orca/palette.py`: upstream colors, copied verbatim.
- `src/gruvbox_orca/themes.py`: which palette role paints which Orca token, syntax scope and terminal color, plus the contrast nudges.
- `src/gruvbox_orca/orca_check.py`: a port of the contrast check Orca's renderer runs before painting a theme.
- `src/gruvbox_orca/build.py`: the `gruvbox-orca` CLI behind `generate`, `report` and the generated-files check.
- `src/gruvbox_orca/cover.py`, `cover.css`: the cover image.
- `tests/`: unit tests.

## Coding Standards

Follow the guidelines repository's coding standards. Project-specific rules:

- Keep palette values identical to upstream; express every adjustment in `themes.py` so `mise run report` can show it.
- Type-hint every public function.

## Testing

- `mise run test` runs the unit tests after the full check.
- Single module: `uv run --locked python -m unittest tests.test_orca_check`.
- When Orca changes its contrast check, compare `orca_check.py` with the new renderer code, then update the port and the expectations in `tests/test_orca_check.py` together.

## Debugging

- `mise run report` prints every adjusted color per variant and any token Orca would drop.
- `uv run gruvbox-orca --check` names each generated file that is out of date.

## Validation

`mise run check` is the entry point for the project's main validation.
It runs the same checks locally that CI runs; do not maintain separate logic.
The prek pre-commit hook runs it on every commit, and the commit-msg hook runs `cog verify`.

## Releases

1. Update `version` in `orca-plugin.json` and merge it to `main`.
2. Tag the merge commit with an annotated `vX.Y.Z` tag matching that version and push the tag.

Releases are immutable: a published tag name can never be reused, even after deleting the release.
