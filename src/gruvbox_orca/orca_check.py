"""A port of the contrast checks Orca's renderer runs on a plugin app theme before painting it.

Orca drops every token in a failing pair and paints its own fallback instead, so a theme that
fails here silently loses colors. Sources (Orca 1.4.x app bundle): shared/plugins/artifacts/
plugin-theme-artifact.js (DERIVED_TOKENS), plugin-theme-css-fallbacks.js, and the renderer's
chat-selection-mix and plugin-monaco-theme chunks.
"""

from dataclasses import dataclass, field

RGBA = tuple[float, float, float, float]

TEXT = 4.5
NON_TEXT = 3.0
RING = 2.0
GIT_STATES = (
    "added",
    "modified",
    "deleted",
    "renamed",
    "untracked",
    "copied",
    "ignored",
)
MONACO_DEFAULT_TOKEN_COLORS = {
    "light": ("#008000", "#a31515", "#0000ff", "#008080", "#098658"),
    "dark": ("#608b4e", "#ce9178", "#569cd6", "#3dc9b0", "#b5cea8"),
}

DERIVED = {
    "--editor-surface": ["--background"],
    "--card": ["--background"],
    "--card-foreground": ["--foreground"],
    "--popover": ["--card", "--background"],
    "--popover-foreground": ["--card-foreground", "--foreground"],
    "--primary": ["--foreground"],
    "--primary-foreground": ["--background"],
    "--muted": ["--secondary"],
    "--secondary": ["--muted"],
    "--muted-foreground": {"mix": 70},
    "--border": {"mix": 16},
    "--accent": {"mix": 12},
    "--accent-foreground": ["--foreground"],
    "--secondary-foreground": ["--foreground"],
    "--input": ["--border"],
    "--ring": ["--primary"],
    "--sidebar": {"mix": 8},
    "--sidebar-foreground": ["--foreground"],
    "--sidebar-primary": ["--primary"],
    "--sidebar-primary-foreground": ["--primary-foreground"],
    "--sidebar-accent": ["--accent"],
    "--sidebar-accent-foreground": ["--accent-foreground"],
    "--sidebar-border": ["--border"],
    "--sidebar-ring": ["--ring"],
    "--worktree-sidebar": ["--sidebar"],
    "--worktree-sidebar-foreground": ["--sidebar-foreground"],
    "--worktree-sidebar-accent": ["--sidebar-accent"],
    "--worktree-sidebar-accent-foreground": ["--sidebar-accent-foreground"],
    "--worktree-sidebar-border": ["--sidebar-border"],
    "--worktree-sidebar-ring": ["--sidebar-ring"],
    "--chart-1": ["--primary"],
}


def tint(token: str, light: float, dark: float, into: str | None = None) -> dict:
    return {
        "light": {"tint": token, "percent": light, "into": into},
        "dark": {"tint": token, "percent": dark, "into": into},
    }


def per_base(light, dark) -> dict:
    return {"light": light, "dark": dark}


CSS_FALLBACKS = {
    "--tab-bar": ["--card"],
    "--tab-active": per_base(["--tab-bar"], {"mix": 6, "into": "--tab-bar"}),
    "--tab-active-foreground": ["--foreground"],
    "--tab-active-indicator": ["--tab-active-foreground"],
    "--tab-inactive": per_base({"mix": 4, "into": "--tab-bar"}, ["--tab-bar"]),
    "--tab-inactive-foreground": ["--muted-foreground"],
    "--worktree-sidebar-active": tint("--worktree-sidebar-foreground", 8, 10),
    "--host-badge": per_base(["--accent"], {"tint": "--accent", "percent": 80, "into": None}),
    "--host-badge-foreground": ["--muted-foreground"],
    "--diff-added": ["--git-decoration-added"],
    "--diff-removed": ["--git-decoration-deleted"],
    "--diff-added-background": tint("--diff-added", 13, 16),
    "--diff-added-emphasis": tint("--diff-added", 15, 20),
    "--diff-added-gutter": tint("--diff-added", 26, 30),
    "--diff-removed-background": tint("--diff-removed", 11, 18),
    "--diff-removed-emphasis": tint("--diff-removed", 15, 20),
    "--diff-removed-gutter": tint("--diff-removed", 22, 32),
    "--chat-diff-added": {"mix": 30, "into": "--diff-added"},
    "--chat-diff-removed": {"mix": 30, "into": "--diff-removed"},
    "--chat-link": {"mix": 30, "into": "--text-link"},
    "--chat-canvas": per_base(["--background"], {"mix": 5}),
    "--chat-foreground": {"mix": 88, "into": "--chat-canvas"},
    "--chat-foreground-strong": {"mix": 98, "into": "--chat-canvas"},
    "--chat-user-message": per_base({"mix": 4, "into": "--chat-canvas"}, {"mix": 7, "into": "--chat-canvas"}),
    "--chat-bold-foreground": ["--chat-foreground"],
    "--chat-muted-foreground": per_base(
        ["--muted-foreground"],
        {"tint": "--muted-foreground", "percent": 83, "into": "--chat-canvas"},
    ),
    "--chat-code-foreground": {"mix": 85, "into": "--chat-canvas"},
    "--chat-inline-code-foreground": ["--chat-code-foreground"],
    "--chat-inline-code": per_base(
        {"mix": 4, "into": "--chat-canvas"},
        {"tint": "--foreground", "percent": 6, "into": None},
    ),
    "--chat-code-block": per_base(
        {"mix": 2, "into": "--chat-canvas"},
        {"tint": "--foreground", "percent": 3.5, "into": None},
    ),
    "--chat-selection": per_base(
        {"tint": "--text-link", "percent": 30, "into": "--chat-canvas"},
        {"tint": "--text-link", "percent": 40, "into": "--chat-canvas"},
    ),
    "--chat-selection-foreground": ["--foreground"],
    "--editor-selection": {"tint": "--ring", "percent": 30, "into": None},
}


def parse(color: str) -> RGBA:
    h = color.lstrip("#")
    alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def luminance(c: RGBA) -> float:
    def channel(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(c[0]) + 0.7152 * channel(c[1]) + 0.0722 * channel(c[2])


def contrast(a: RGBA, b: RGBA) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def composite(top: RGBA, bottom: RGBA) -> RGBA:
    a = top[3]
    return (
        top[0] * a + bottom[0] * (1 - a),
        top[1] * a + bottom[1] * (1 - a),
        top[2] * a + bottom[2] * (1 - a),
        1.0,
    )


def mix(a: RGBA, b: RGBA, percent: float) -> RGBA:
    r = percent / 100
    return tuple(a[i] * r + b[i] * (1 - r) for i in range(4))


@dataclass
class Pair:
    surface: str
    text: str
    floor: float = TEXT
    over: list[str] = field(default_factory=list)
    drop: list[str] | None = None
    surface_source: str | None = None
    no_worse_than_over: bool = False

    @property
    def dropped(self) -> list[str]:
        return self.drop if self.drop is not None else [self.surface, self.text]


def chat(
    surface: str,
    text: str,
    drop: list[str] | None = None,
    over: list[str] | None = None,
) -> Pair:
    return Pair(surface, text, over=[*(over or []), "--chat-canvas"], drop=drop)


def pairs() -> list[Pair]:
    out = [
        Pair(s, t)
        for s, t in [
            ("--background", "--foreground"),
            ("--background", "--muted-foreground"),
            ("--editor-surface", "--foreground"),
            ("--editor-surface", "--muted-foreground"),
            ("--card", "--card-foreground"),
            ("--popover", "--popover-foreground"),
            ("--primary", "--primary-foreground"),
            ("--secondary", "--secondary-foreground"),
            ("--muted", "--muted-foreground"),
            ("--accent", "--accent-foreground"),
            ("--sidebar", "--sidebar-foreground"),
            ("--sidebar-primary", "--sidebar-primary-foreground"),
            ("--sidebar-accent", "--sidebar-accent-foreground"),
            ("--worktree-sidebar", "--worktree-sidebar-foreground"),
            ("--worktree-sidebar-accent", "--worktree-sidebar-accent-foreground"),
        ]
    ]
    out += [
        Pair(
            "--worktree-sidebar-active",
            "--worktree-sidebar-foreground",
            drop=["--worktree-sidebar-active"],
            over=["--worktree-sidebar"],
        ),
        Pair("--host-badge", "--host-badge-foreground", over=["--worktree-sidebar"]),
        Pair("--tab-active", "--tab-active-foreground"),
        Pair("--tab-inactive", "--tab-inactive-foreground"),
        Pair("--tab-inactive", "--tab-active-foreground"),
        chat("--chat-user-message", "--chat-foreground-strong", ["--chat-user-message"]),
    ]
    for side in ("added", "removed"):

        def diff(part: str, side: str = side) -> Pair:
            return Pair(
                f"--diff-{side}-{part}",
                "--foreground",
                drop=[f"--diff-{side}-{part}"],
                surface_source=f"--diff-{side}",
                over=["--editor-surface"],
            )

        chat_text = Pair(
            **{
                **diff("background").__dict__,
                "text": f"--chat-diff-{side}",
                "over": ["--chat-canvas"],
            }
        )
        out += [
            diff("background"),
            diff("emphasis"),
            chat_text,
            chat(
                f"--diff-{side}-background",
                f"--chat-diff-{side}",
                ["--chat-code-block"],
                ["--chat-code-block"],
            ),
        ]
    out += [
        Pair("--chat-canvas", "--chat-bold-foreground"),
        Pair("--chat-canvas", "--chat-muted-foreground"),
        chat("--chat-user-message", "--chat-bold-foreground", ["--chat-bold-foreground"]),
    ]
    for under in ([], ["--chat-user-message"]):
        out += [
            chat("--chat-inline-code", "--chat-inline-code-foreground", None, under),
            chat("--chat-inline-code", "--chat-link", ["--chat-inline-code"], under),
        ]
    out += [
        chat("--chat-code-block", "--chat-code-foreground", ["--chat-code-block"]),
        chat("--chat-code-block", "--chat-foreground", ["--chat-code-block"]),
    ]
    for dropped in ("--chat-code-block", "--chat-muted-foreground"):
        p = chat("--chat-code-block", "--chat-muted-foreground", [dropped])
        p.no_worse_than_over = True
        out.append(p)
    for under in (
        [],
        ["--chat-user-message"],
        ["--chat-code-block"],
        ["--chat-inline-code"],
        ["--chat-inline-code", "--chat-user-message"],
    ):
        out.append(chat("--chat-selection", "--chat-selection-foreground", None, under))
    out += [
        Pair("--editor-surface", "--text-link", drop=["--text-link"]),
        Pair(
            "--editor-selection",
            "--foreground",
            drop=["--editor-selection"],
            over=["--editor-surface"],
        ),
        chat("--chat-user-message", "--chat-link", ["--chat-user-message"]),
    ]
    out += [
        Pair(
            "--sidebar",
            f"--git-decoration-{s}",
            NON_TEXT,
            drop=[f"--git-decoration-{s}"],
        )
        for s in GIT_STATES
    ]
    return out


RINGS = [
    ("--ring", "--background"),
    ("--sidebar-ring", "--sidebar"),
    ("--worktree-sidebar-ring", "--worktree-sidebar"),
    ("--tab-active-indicator", "--tab-active"),
    ("--tab-active-indicator", "--sidebar"),
]
BORDERS = {
    "--border",
    "--input",
    "--sidebar-border",
    "--worktree-sidebar-border",
    "--worktree-sidebar-active-border",
    "--split-divider",
    "--split-divider-hover",
}


def complete(tokens: dict[str, str]) -> dict[str, str]:
    """DERIVED_TOKENS as plain hex, so the check sees what Orca registers."""
    out = dict(tokens)
    for token, rule in DERIVED.items():
        if token in out:
            continue
        if isinstance(rule, dict):
            c = mix(parse(out["--foreground"]), parse(out["--background"]), rule["mix"])
            out[token] = "#" + "".join(f"{round(v):02x}" for v in c[:3])
        else:
            source = next((out[s] for s in rule if s in out), None)
            if source:
                out[token] = source
    return out


def dropped_tokens(tokens: dict[str, str], base: str) -> list[str]:
    """Tokens Orca would drop, in the order it drops them."""
    theme = complete(tokens)
    kept = {t: parse(v) for t, v in theme.items() if not (t in BORDERS and parse(v)[3] < 0.05)}
    dropped: list[str] = []

    def resolve(token: str, seen: frozenset = frozenset()) -> RGBA | None:
        if token in kept:
            return kept[token]
        if token in seen:
            return None
        rule = CSS_FALLBACKS.get(token)
        if rule is None:
            return None
        if isinstance(rule, dict) and "light" in rule:
            rule = rule[base]
        seen = seen | {token}
        if isinstance(rule, list):
            return next((c for c in (resolve(s, seen) for s in rule) if c), None)
        if "tint" in rule:
            t = resolve(rule["tint"], seen)
            if t is None:
                return None
            if not rule.get("into"):
                return (t[0], t[1], t[2], t[3] * rule["percent"] / 100)
            into = resolve(rule["into"], seen)
            return mix(t, into, rule["percent"]) if into else None
        fg, into = (
            resolve("--foreground", seen),
            resolve(rule.get("into") or "--background", seen),
        )
        return mix(fg, into, rule["mix"]) if fg and into else None

    def stack(tokens_: list[str]) -> RGBA | None:
        acc = None
        for t in reversed(tokens_):
            c = resolve(t)
            acc = composite(c, acc) if c and acc and acc[3] == 1 else c
        return acc

    def drop(*names: str) -> bool:
        hit = False
        for n in names:
            if n in kept:
                del kept[n]
                dropped.append(n)
                hit = True
        return hit

    checks = pairs()
    changed = True
    while changed:
        changed = False
        for p in checks:
            names = [*p.dropped, p.surface_source] if p.surface_source and p.surface not in theme else p.dropped
            if not any(n in kept for n in names):
                continue
            text, surface, under = resolve(p.text), resolve(p.surface), stack(p.over)
            painted = composite(surface, under) if surface and under and under[3] == 1 else surface
            floor = p.floor
            if p.no_worse_than_over and under and under[3] == 1 and text and text[3] == 1:
                floor = min(floor, contrast(under, text))
            if painted and text and (painted[3] < 1 or text[3] < 1 or contrast(painted, text) < floor):
                changed = drop(*names) or changed
        for token, surface_token in RINGS:
            ring = kept.get(token)
            surface = resolve(surface_token)
            if ring and surface and contrast(composite(ring, surface), surface) < RING:
                changed = drop(token) or changed
    return dropped


def monaco_problems(tokens: dict[str, str], base: str, syntax: list[str]) -> list[str]:
    editor = parse(tokens.get("--editor-surface", tokens["--background"]))
    problems = []
    if contrast(parse(tokens["--foreground"]), editor) < TEXT:
        problems.append("foreground under 4.5:1 on the editor: Orca skips the whole Monaco theme")
    problems += [
        f"Monaco default {c} under 3:1 on the editor: Orca skips the whole Monaco theme"
        for c in MONACO_DEFAULT_TOKEN_COLORS[base]
        if contrast(parse(c), editor) < NON_TEXT
    ]
    problems += [
        f"token color {c} under 3:1 on the editor: Monaco drops it"
        for c in syntax
        if contrast(composite(parse(c), editor), editor) < NON_TEXT
    ]
    return problems
