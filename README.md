<div align="center">

# Gruvbox Material for Orca

Every [Gruvbox Material](https://github.com/sainnhe/gruvbox-material) variant as an Orca app, syntax and terminal theme.

[Installation](#-installation) | [Usage](#-usage) | [Features](#-features) | [Development](#-development)

[![Check](https://img.shields.io/github/actions/workflow/status/fang2hou/orca-gruvbox-material-theme/check.yml?branch=main&label=check&style=flat-square)](https://github.com/fang2hou/orca-gruvbox-material-theme/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](./LICENSE)

</div>

The plugin ships all nine upstream combinations (hard, medium and soft backgrounds with the Material, Mix and Original foreground palettes) in dark and light. Colors come from sainnhe's palette definitions; a few are nudged the smallest amount needed so Orca's own contrast check keeps every color the theme sets.

![Gruvbox Material Dark and Light (Medium, Mix) in Orca, with swatches of every variant](images/cover.png)

## 📦 Installation

Requires Orca 1.4.245 or newer.

```sh
orca plugin install fang2hou/orca-gruvbox-material-theme
```

Installed copies update with `orca plugin update fang2hou.gruvbox-material-theme`.

## 🚀 Usage

1. Open Orca's Appearance settings and pick a theme such as **Gruvbox Material Dark (Medium, Mix)** for the dark and light slots.
2. Pick the theme of the same name in the terminal settings.

Theme names follow upstream's options: the background (`hard`, `medium`, `soft`) sets the contrast, and the foreground (`material`, `mix`, `original`) sets the accent palette.

## ✨ Features

| Feature | Details |
| --- | --- |
| App theme | Uniform `bg0` panels, a recessed tab strip, raised menus, and every public Orca color token set from the palette |
| Syntax colors | Gruvbox Material's own highlight groups: red keywords, aqua strings, bold green functions, bold yellow types, blue properties, plain variables |
| Markdown and chat | Orange headings, red list markers, aqua inline code, and diff colors that stay readable in chat |
| Terminal theme | Upstream's terminal mapping, with a dim bright black for autosuggestions and a readable block cursor |
| Contrast-checked | Every theme passes a port of Orca's renderer contrast check, so Orca never swaps a color for its fallback |
| Tinted sidebar aware | Hover fills stay visible when Orca's Tinted left sidebar is on |

Design decisions and the full palette mapping are in [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🛠️ Development

Requires [mise](https://mise.jdx.dev/) on macOS or Linux; the toolchain is pinned in `mise.toml`.

```sh
mise install
mise run generate
mise run test
```

`mise run generate` rewrites `themes/`, `terminal/` and the manifest entries, and `mise run test` runs the full check and the unit tests. See [DEVELOPMENT.md](./DEVELOPMENT.md) for every task and the release steps.

## 📄 License

[MIT](./LICENSE)

Gruvbox Material colors are by sainnhe (MIT). The Orca token and scope mapping started from [piter75/orca-gruvbox-material-theme](https://github.com/piter75/orca-gruvbox-material-theme) (MIT). Both notices are in [LICENSE](./LICENSE).
