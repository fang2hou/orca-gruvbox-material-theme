"""Render images/cover.png from the theme JSON, so the cover always shows the shipped colors.

Playwright and its headless browser are fetched on first run (`mise run cover`), on any OS.
"""

import html
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Error, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
WIDTH, HEIGHT = 1600, 1000

CODE = [
    [("comment", "// Resolve the palette for the active workspace.")],
    [
        ("keyword", "import"),
        ("plain", " { "),
        ("variable", "createTheme"),
        ("plain", " } "),
        ("keyword", "from"),
        ("plain", " "),
        ("string", "'./theme'"),
    ],
    [],
    [
        ("keyword", "export"),
        ("plain", " "),
        ("storage", "interface"),
        ("plain", " "),
        ("type", "Workspace"),
        ("plain", " {"),
    ],
    [
        ("plain", "  "),
        ("property", "name"),
        ("operator", ":"),
        ("plain", " "),
        ("type", "string"),
    ],
    [
        ("plain", "  "),
        ("property", "tabs"),
        ("operator", ":"),
        ("plain", " "),
        ("type", "number"),
    ],
    [("plain", "}")],
    [],
    [
        ("keyword", "export"),
        ("plain", " "),
        ("storage", "function"),
        ("plain", " "),
        ("function", "openWorkspace"),
        ("plain", "("),
        ("variable", "ws"),
        ("operator", ":"),
        ("plain", " "),
        ("type", "Workspace"),
        ("plain", ") {"),
    ],
    [
        ("plain", "  "),
        ("storage", "const"),
        ("plain", " "),
        ("variable", "theme"),
        ("plain", " "),
        ("operator", "="),
        ("plain", " "),
        ("function", "createTheme"),
        ("plain", "({ "),
        ("property", "contrast"),
        ("operator", ":"),
        ("plain", " "),
        ("number", "0.92"),
        ("plain", " })"),
    ],
    [
        ("plain", "  "),
        ("keyword", "if"),
        ("plain", " ("),
        ("variable", "ws"),
        ("plain", "."),
        ("property", "tabs"),
        ("plain", " "),
        ("operator", ">"),
        ("plain", " "),
        ("number", "12"),
        ("plain", ") "),
        ("keyword", "return"),
        ("plain", " "),
        ("variable", "theme"),
        ("plain", "."),
        ("function", "compact"),
        ("plain", "()"),
    ],
    [
        ("plain", "  "),
        ("keyword", "return"),
        ("plain", " { "),
        ("operator", "..."),
        ("variable", "theme"),
        ("plain", ", "),
        ("property", "title"),
        ("operator", ":"),
        ("plain", " "),
        ("variable", "ws"),
        ("plain", "."),
        ("property", "name"),
        ("plain", " "),
        ("operator", "+"),
        ("plain", " "),
        ("string", "' \u2014 Orca'"),
        ("plain", " }"),
    ],
    [("plain", "}")],
]
SCOPES = {
    "comment": "Comments",
    "keyword": "Keywords",
    "storage": "Storage modifiers",
    "operator": "Operators",
    "string": "Strings",
    "function": "Functions",
    "type": "Types",
    "number": "Numbers, booleans and built-in constants",
    "variable": "Variables and parameters",
    "property": "Properties and keys",
}
TREE = [
    (0, "src", False),
    (1, "components", False),
    (2, "Sidebar.tsx", False),
    (2, "theme.ts", True),
    (1, "server", False),
    (2, "router.ts", False),
    (0, "package.json", False),
    (0, "README.md", False),
    (0, "tsconfig.json", False),
]

FEATURED = "medium-mix"
CSS_VARIABLES = {
    "--bg": "--background",
    "--fg": "--foreground",
    "--border": "--border",
    "--muted": "--muted",
    "--muted-fg": "--muted-foreground",
    "--sidebar-border": "--worktree-sidebar-border",
    "--sidebar-accent": "--sidebar-accent",
    "--tab-bar": "--tab-bar",
    "--tab-active": "--tab-active",
    "--tab-active-fg": "--tab-active-foreground",
    "--tab-indicator": "--tab-active-indicator",
    "--tab-inactive": "--tab-inactive",
    "--tab-inactive-fg": "--tab-inactive-foreground",
}


def load(slug: str) -> tuple[dict, dict, dict]:
    theme = json.loads((ROOT / f"themes/gruvbox-material-{slug}.json").read_text())
    terminal = json.loads((ROOT / f"terminal/gruvbox-material-{slug}.json").read_text())["terminal"]
    syntax = {rule["name"]: rule["settings"] for rule in theme["tokenColors"]}
    return theme["tokens"], syntax, terminal


def theme_variables(tokens: dict) -> str:
    return ";".join(f"{name}:{tokens[token]}" for name, token in CSS_VARIABLES.items())


def colored(text: str, color: str, css: str = "") -> str:
    return f'<span style="color:{color};{css}">{html.escape(text)}</span>'


def code_line(number: int, parts: list[tuple[str, str]], syntax: dict) -> str:
    spans = []
    for kind, text in parts:
        if kind == "plain":
            spans.append(html.escape(text))
            continue
        rule = syntax[SCOPES[kind]]
        font_style = rule.get("fontStyle") or ""
        css = ("font-style:italic;" if "italic" in font_style else "") + (
            "font-weight:700;" if "bold" in font_style else ""
        )
        spans.append(colored(text, rule["foreground"], css))
    return f'<div class="ln"><span class="no">{number}</span>{"".join(spans)}</div>'


def terminal_lines(term: dict) -> str:
    prompt = colored("❯", term["green"])
    lines = [
        f"{colored('~/atlas', term['blue'])} {colored('main', term['magenta'])}",
        f"{prompt} git status --short{colored(' --branch', term['brightBlack'])}",
        f"{colored(' M', term['yellow'])} src/theme.ts",
        f"{colored(' D', term['red'])} src/palette.ts",
        f'{prompt} <span class="cursor" style="background:{term["cursor"]}"></span>',
    ]
    return "".join(f"<div>{line}</div>" for line in lines)


def window(mode: str) -> str:
    tokens, syntax, term = load(f"{mode}-{FEATURED}")
    title = f"Gruvbox Material {mode.title()} (Medium, Mix)"
    tree = "".join(
        f'<div class="row{" sel" if selected else ""}" style="padding-left:{14 + depth * 16}px">'
        f'<span class="dot"></span>{html.escape(name)}</div>'
        for depth, name, selected in TREE
    )
    code = "".join(code_line(n, parts, syntax) for n, parts in enumerate(CODE, 1))
    lights = "".join(f'<i style="background:{c}"></i>' for c in ("#ff5f57", "#febc2e", "#28c840"))
    tabs = '<span class="tab on">theme.ts</span><span class="tab">router.ts</span><span class="tab">README.md</span>'
    return f"""
<div class="win {mode}" style="{theme_variables(tokens)}">
  <div class="bar"><span class="lights">{lights}</span><span>atlas — Orca</span><span class="name">{title}</span></div>
  <div class="body">
    <div class="side"><div class="head">EXPLORER</div>{tree}<div class="badge">BETA</div></div>
    <div class="main">
      <div class="tabs">{tabs}</div>
      <div class="code">{code}</div>
      <div class="term">
        <div class="thead">TERMINAL&nbsp;&nbsp;&nbsp;zsh — atlas</div>
        <div class="tbody" style="color:{term["foreground"]}">{terminal_lines(term)}</div>
      </div>
    </div>
  </div>
</div>"""


def page() -> str:
    css = (Path(__file__).parent / "cover.css").read_text()
    body = window("dark") + window("light")
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'


def screenshot(markup: str, out: Path) -> None:
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Error:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium-headless-shell"], check=True)
            browser = playwright.chromium.launch()
        tab = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        tab.set_content(markup, wait_until="load")
        tab.screenshot(path=out)
        browser.close()


def main() -> None:
    out = ROOT / "images/cover.png"
    screenshot(page(), out)
    print(out)


if __name__ == "__main__":
    main()
