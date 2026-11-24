"""Maps Gruvbox Material palette roles onto Orca's app, syntax and terminal theme formats."""

from dataclasses import dataclass, field

from gruvbox_orca import orca_check
from gruvbox_orca.palette import BACKGROUNDS, FOREGROUNDS, MODES, palette

# Orca's defaults for the Tinted left sidebar: color-mix(tint 8%, --background), hover = fg 9% over it.
ORCA_TINT_COLOR = "#18181b"
ORCA_TINT_OPACITY = 0.08
ORCA_TINT_HOVER = 0.09

TEXT_CONTRAST = orca_check.TEXT
SYNTAX_CONTRAST = orca_check.NON_TEXT
# A ghost-button hover must stay visible on the tinted sidebar, where Light bg3 nearly vanished.
ACCENT_ON_TINT_CONTRAST = 1.15

# Tokens Orca may drop at the contrast floor, mapped to the token whose color decides the pair.
SETTLE_TARGETS = {
    "--chat-inline-code-foreground": "--chat-inline-code-foreground",
    "--text-link": "--text-link",
    "--diff-added-background": "--diff-added",
    "--diff-removed-background": "--diff-removed",
}

# Roles follow gruvbox-material's own highlight groups as tuned in the author's Neovim setup.
# Orca's Monaco maps every Monarch `identifier` to `variable`, so variables stay fg0. A deeper
# scope that sets fontStyle "" clears bold inherited from a broader one.
SYNTAX_RULES = [
    ("Comments", ["comment", "punctuation.definition.comment"], "grey1", "italic"),
    (
        "Variables and parameters",
        ["variable", "variable.parameter", "variable.other.constant", "constant.other"],
        "fg0",
        None,
    ),
    (
        "Properties and keys",
        [
            "variable.other.property",
            "variable.other.object.property",
            "support.variable.property",
            "meta.object-literal.key",
            "support.type.property-name",
        ],
        "blue",
        "",
    ),
    ("Built-in variables", ["variable.language", "support.variable", "support.constant"], "purple", None),
    ("Constants", ["constant"], "aqua", None),
    (
        "Numbers, booleans and built-in constants",
        ["constant.numeric", "constant.language", "keyword.other.unit"],
        "purple",
        None,
    ),
    ("Characters", ["constant.character"], "aqua", None),
    ("Keywords", ["keyword", "storage.type"], "red", None),
    ("Storage modifiers", ["storage.modifier"], "orange", None),
    ("Operators", ["keyword.operator"], "orange", None),
    (
        "Preprocessor",
        ["meta.preprocessor", "keyword.control.directive", "entity.name.function.preprocessor"],
        "purple",
        None,
    ),
    (
        "Strings",
        ["string", "punctuation.definition.string", "markup.inline.raw", "markup.raw", "markup.fenced_code"],
        "aqua",
        None,
    ),
    (
        "Escapes and regular expressions",
        ["constant.character.escape", "string.regexp", "constant.other.character-class.regexp"],
        "green",
        None,
    ),
    ("Functions", ["entity.name.function", "support.function"], "green", "bold"),
    (
        "Types",
        ["entity.name.type", "entity.name.class", "entity.other.inherited-class", "support.type", "support.class"],
        "yellow",
        "bold",
    ),
    ("Namespaces", ["entity.name.namespace", "entity.name.type.module"], "yellow", ""),
    ("Punctuation", ["punctuation", "meta.brace"], "fg0", None),
    ("Delimiters", ["punctuation.separator", "punctuation.terminator", "punctuation.accessor"], "grey1", None),
    (
        "Embedded punctuation",
        [
            "punctuation.definition.template-expression",
            "punctuation.section.embedded",
            "punctuation.definition.interpolation",
        ],
        "blue",
        None,
    ),
    ("Tags", ["entity.name.tag"], "orange", None),
    ("Tag delimiters and attributes", ["punctuation.definition.tag", "entity.other.attribute-name"], "green", None),
    ("Decorators", ["meta.decorator", "entity.name.function.decorator", "punctuation.decorator"], "purple", ""),
    ("Labels", ["entity.name.label", "punctuation.definition.label"], "orange", None),
    ("Headings", ["markup.heading", "entity.name.section", "punctuation.definition.heading"], "orange", "bold"),
    ("Bold", ["markup.bold"], None, "bold"),
    ("Italic", ["markup.italic"], None, "italic"),
    ("Strikethrough", ["markup.strikethrough"], "grey1", "strikethrough"),
    ("Links", ["markup.underline.link", "string.other.link"], "blue", "underline"),
    ("Quotes", ["markup.quote"], "grey1", "italic"),
    (
        "List markers",
        ["punctuation.definition.list", "markup.list.numbered.bullet", "beginning.punctuation.definition.list"],
        "red",
        None,
    ),
    ("Separators", ["meta.separator"], "grey1", None),
    ("Inserted", ["markup.inserted"], "green", None),
    ("Deleted", ["markup.deleted"], "red", None),
    ("Changed", ["markup.changed"], "orange", None),
    ("Invalid", ["invalid"], "red", None),
]
SYNTAX_ROLES = sorted({role for _, _, role, _ in SYNTAX_RULES if role})


def rgb(color: str) -> list[int]:
    return [int(color[i : i + 2], 16) for i in (1, 3, 5)]


def mix(base: str, other: str, amount: float) -> str:
    return "#" + "".join(
        f"{round(a * (1 - amount) + b * amount):02x}" for a, b in zip(rgb(base), rgb(other), strict=True)
    )


def contrast(a: str, b: str) -> float:
    return orca_check.contrast(orca_check.parse(a), orca_check.parse(b))


def nudge(color: str, toward: str, surfaces: list[str], floor: float) -> str:
    """The smallest 1% step from color toward `toward` that meets floor on every surface."""
    for step in range(101):
        candidate = mix(color, toward, step / 100)
        if all(contrast(candidate, s) >= floor for s in surfaces):
            return candidate
    raise ValueError(f"{color} cannot reach {floor}:1 toward {toward}")


@dataclass
class Variant:
    background: str
    foreground: str
    mode: str
    adjustments: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.p = palette(self.background, self.foreground, self.mode)

    @property
    def slug(self) -> str:
        return f"gruvbox-material-{self.mode}-{self.background}-{self.foreground}"

    @property
    def title(self) -> str:
        return f"Gruvbox Material {self.mode.title()} ({self.background.title()}, {self.foreground.title()})"

    def note(self, role: str, before: str, after: str) -> str:
        if before != after:
            self.adjustments.append(f"{role}: {before} -> {after}")
        return after

    def readable(self, role: str, color: str, surfaces: list[str], floor: float = TEXT_CONTRAST) -> str:
        return self.note(role, color, nudge(color, self.p["fg0"], surfaces, floor))

    def tokens(self) -> dict[str, str]:
        p, dark = self.p, self.mode == "dark"
        bg0, fg0 = p["bg0"], p["fg0"]
        tint = mix(bg0, ORCA_TINT_COLOR, ORCA_TINT_OPACITY)
        tint_hover = mix(tint, fg0, ORCA_TINT_HOVER)

        popover = p["bg1"]
        muted = p["bg_current_word"] if dark else p["bg4"]
        sidebar_accent = p["bg3"]
        accent = p["bg3"] if dark else self.readable("accent", p["bg5"], [tint], ACCENT_ON_TINT_CONTRAST)
        border = p["bg3"] if dark else p["bg5"]
        tab_bar = p["bg_dim"]

        muted_fg = self.readable(
            "muted-foreground",
            p["grey2"],
            [bg0, tab_bar, popover, muted, accent, sidebar_accent, tint, tint_hover],
        )
        primary_fg = self.primary_foreground()
        tokens = {
            "--background": bg0,
            "--editor-surface": bg0,
            "--foreground": fg0,
            "--card": bg0,
            "--card-foreground": fg0,
            "--popover": popover,
            "--popover-foreground": fg0,
            "--primary": p["green"],
            "--primary-foreground": primary_fg,
            "--secondary": muted,
            "--secondary-foreground": fg0,
            "--muted": muted,
            "--muted-foreground": muted_fg,
            "--accent": accent,
            "--accent-foreground": fg0,
            "--border": border,
            "--input": p["bg1"] if dark else p["bg3"],
            "--ring": p["green"],
            "--sidebar": bg0,
            "--sidebar-foreground": fg0,
            "--sidebar-primary": p["green"],
            "--sidebar-primary-foreground": primary_fg,
            "--sidebar-accent": sidebar_accent,
            "--sidebar-accent-foreground": fg0,
            "--sidebar-border": border,
            "--sidebar-ring": p["green"],
            "--worktree-sidebar": bg0,
            "--worktree-sidebar-border": border,
            "--chart-1": p["green"],
            "--chart-2": p["orange"],
            "--chart-3": p["blue"],
            "--chart-4": p["purple"],
            "--chart-5": p["yellow"],
            "--tab-bar": tab_bar,
            "--tab-active": bg0,
            "--tab-active-foreground": fg0,
            "--tab-active-indicator": p["green"],
            "--tab-inactive": tab_bar,
            "--tab-inactive-foreground": muted_fg,
            "--split-divider": border,
            "--split-divider-hover": p["green"],
            "--chat-bold-foreground": fg0,
            "--chat-inline-code-foreground": p["aqua"],
            "--text-link": self.readable("text-link", p["blue"], [bg0, popover]),
            "--editor-selection": fg0 + ("26" if dark else "1f"),
        }
        for side, hue in (("added", "green"), ("removed", "red")):
            tokens |= {
                f"--diff-{side}": p[hue],
                f"--diff-{side}-background": p[f"bg_diff_{hue}"],
                f"--diff-{side}-emphasis": p[f"bg_visual_{hue}"],
                f"--diff-{side}-gutter": mix(bg0, p[hue], 0.3),
            }
        tokens |= {
            "--git-decoration-added": p["green"],
            "--git-decoration-modified": p["orange"],
            "--git-decoration-deleted": p["red"],
            "--git-decoration-renamed": p["blue"],
            "--git-decoration-untracked": p["green"],
            "--git-decoration-copied": p["aqua"],
            "--git-decoration-ignored": self.readable("git ignored", p["grey1"], [bg0], SYNTAX_CONTRAST),
        }
        return self.settle(tokens)

    def settle(self, tokens: dict[str, str]) -> dict[str, str]:
        """Steps the token behind each Orca drop toward fg0 until Orca's check keeps everything."""
        origin: dict[str, tuple[str, int]] = {}
        for _ in range(101 * len(SETTLE_TARGETS)):
            dropped = orca_check.dropped_tokens(tokens, self.mode)
            target = next((SETTLE_TARGETS[t] for t in dropped if t in SETTLE_TARGETS), None)
            if target is None:
                break
            start, steps = origin.get(target, (tokens[target], 0))
            origin[target] = (start, steps + 1)
            tokens[target] = mix(start, self.p["fg0"], (steps + 1) / 100)
        for target, (start, _) in origin.items():
            self.note(target.removeprefix("--"), start, tokens[target])
        return tokens

    def primary_foreground(self) -> str:
        green, bg0 = self.p["green"], self.p["bg0"]
        fallback = "#ffffff" if self.mode == "light" else self.p["bg_dim"]
        for candidate in (bg0, fallback):
            if contrast(candidate, green) >= TEXT_CONTRAST:
                return self.note("primary-foreground", bg0, candidate)
        raise ValueError(f"{self.slug}: no primary foreground reaches {TEXT_CONTRAST}:1 on {green}")

    def app_theme(self) -> dict:
        p = self.p
        colors = {role: self.readable(f"syntax {role}", p[role], [p["bg0"]], SYNTAX_CONTRAST) for role in SYNTAX_ROLES}
        rules = []
        for name, scope, role, style in SYNTAX_RULES:
            settings = {}
            if role:
                settings["foreground"] = colors[role]
            if style is not None:
                settings["fontStyle"] = style
            rules.append({"name": name, "scope": scope, "settings": settings})
        return {"base": self.mode, "tokens": self.tokens(), "tokenColors": rules}

    def terminal_theme(self) -> dict:
        p, dark = self.p, self.mode == "dark"
        black, white = (p["bg5"], p["fg0"]) if dark else (p["fg0"], p["bg5"])
        colors = {
            "black": black,
            "red": p["red"],
            "green": p["green"],
            "yellow": p["yellow"],
            "blue": p["blue"],
            "magenta": p["purple"],
            "cyan": p["aqua"],
            "white": white,
        }
        terminal = {
            "background": p["bg0"],
            "foreground": p["fg0"],
            "cursor": p["fg0"],
            "cursorAccent": p["bg0"],
            "selectionBackground": p["bg3"],
        }
        for name, color in colors.items():
            terminal[name] = color
            # Shells draw dimmed text with bright black; upstream's value equals fg0 in Light.
            terminal["bright" + name.title()] = p["grey1"] if name == "black" else color
        return {"schemaVersion": 1, "mode": self.mode, "terminal": terminal}


def problems(theme: dict) -> list[str]:
    """Everything Orca would discard from a generated app theme."""
    dropped = orca_check.dropped_tokens(theme["tokens"], theme["base"])
    syntax = [r["settings"]["foreground"] for r in theme["tokenColors"] if "foreground" in r["settings"]]
    return [f"Orca drops {t}" for t in dropped] + orca_check.monaco_problems(theme["tokens"], theme["base"], syntax)


def variants() -> list[Variant]:
    return [Variant(b, f, m) for m in MODES for b in BACKGROUNDS for f in FOREGROUNDS]
