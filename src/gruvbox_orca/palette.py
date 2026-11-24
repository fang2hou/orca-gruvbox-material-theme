"""Gruvbox Material colors, copied from sainnhe/gruvbox-material autoload/gruvbox_material.vim."""

BACKGROUNDS = ("hard", "medium", "soft")
FOREGROUNDS = ("material", "mix", "original")
MODES = ("dark", "light")

BG_KEYS = (
    "bg_dim",
    "bg0",
    "bg1",
    "bg3",
    "bg4",
    "bg5",
    "bg_visual_red",
    "bg_visual_green",
    "bg_diff_red",
    "bg_diff_green",
    "bg_current_word",
)
FG_KEYS = ("fg0", "red", "orange", "yellow", "green", "aqua", "blue", "purple")

BG_PALETTES = {
    ("hard", "dark"): "#141617 #1d2021 #282828 #3c3836 #3c3836 #504945 #442e2d #333e34 #3c1f1e #32361a #32302f",
    ("hard", "light"): "#f3eac7 #f9f5d7 #f5edca #f2e5bc #eee0b7 #ebdbb2 #f0ddc3 #dde5c2 #f8e4c9 #e4edc8 #f3eac7",
    ("medium", "dark"): "#1b1b1b #282828 #32302f #45403d #45403d #5a524c #4c3432 #3b4439 #402120 #34381b #3c3836",
    ("medium", "light"): "#f2e5bc #fbf1c7 #f4e8be #eee0b7 #e5d5ad #ddccab #f1d9b5 #dee2b6 #f9e0bb #e6eabc #f2e5bc",
    ("soft", "dark"): "#252423 #32302f #3c3836 #504945 #504945 #665c54 #543937 #424a3e #472322 #3d4220 #45403d",
    ("soft", "light"): "#ebdbb2 #f2e5bc #eddeb5 #e6d5ae #dac9a5 #d5c4a1 #efd2b3 #d7d9ae #f7d9b9 #dfe1b4 #ebdbb2",
}
FG_PALETTES = {
    ("material", "dark"): "#d4be98 #ea6962 #e78a4e #d8a657 #a9b665 #89b482 #7daea3 #d3869b",
    ("material", "light"): "#654735 #c14a4a #c35e0a #b47109 #6c782e #4c7a5d #45707a #945e80",
    ("mix", "dark"): "#e2cca9 #f2594b #f28534 #e9b143 #b0b846 #8bba7f #80aa9e #d3869b",
    ("mix", "light"): "#514036 #af2528 #b94c07 #b4730e #72761e #477a5b #266b79 #924f79",
    ("original", "dark"): "#ebdbb2 #fb4934 #fe8019 #fabd2f #b8bb26 #8ec07c #83a598 #d3869b",
    ("original", "light"): "#3c3836 #9d0006 #af3a03 #b57614 #79740e #427b58 #076678 #8f3f71",
}
GREYS = {
    "dark": {"grey0": "#7c6f64", "grey1": "#928374", "grey2": "#a89984"},
    "light": {"grey0": "#a89984", "grey1": "#928374", "grey2": "#7c6f64"},
}


def palette(background: str, foreground: str, mode: str) -> dict[str, str]:
    return {
        **dict(zip(BG_KEYS, BG_PALETTES[background, mode].split(), strict=True)),
        **dict(zip(FG_KEYS, FG_PALETTES[foreground, mode].split(), strict=True)),
        **GREYS[mode],
    }
