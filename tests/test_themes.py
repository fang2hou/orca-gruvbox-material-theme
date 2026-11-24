import unittest

from gruvbox_orca.palette import palette
from gruvbox_orca.themes import Variant, contrast, nudge, problems, variants


class NudgeTest(unittest.TestCase):
    def test_passing_color_is_unchanged(self) -> None:
        self.assertEqual(nudge("#e2cca9", "#ffffff", ["#282828"], 4.5), "#e2cca9")

    def test_failing_color_moves_the_smallest_step_that_passes(self) -> None:
        moved = nudge("#a89984", "#e2cca9", ["#45403d"], 4.5)
        self.assertGreaterEqual(contrast(moved, "#45403d"), 4.5)
        self.assertEqual(moved, "#bbaa90")


class VariantTest(unittest.TestCase):
    def test_every_variant_is_unique_and_survives_orcas_checks(self) -> None:
        all_variants = variants()
        self.assertEqual(len({v.slug for v in all_variants}), 18)
        for variant in all_variants:
            with self.subTest(variant=variant.slug):
                self.assertEqual(problems(variant.app_theme()), [])

    def test_surfaces_and_text_come_straight_from_the_palette(self) -> None:
        source = palette("medium", "mix", "dark")
        tokens = Variant("medium", "mix", "dark").app_theme()["tokens"]
        self.assertEqual(tokens["--background"], source["bg0"])
        self.assertEqual(tokens["--foreground"], source["fg0"])
        self.assertEqual(tokens["--git-decoration-modified"], source["orange"])

    def test_light_accent_stays_visible_on_orcas_tinted_sidebar(self) -> None:
        variant = Variant("hard", "mix", "light")
        accent = variant.app_theme()["tokens"]["--accent"]
        self.assertNotEqual(accent, variant.p["bg5"])
        self.assertTrue(any(a.startswith("accent:") for a in variant.adjustments))

    def test_terminal_bright_black_stays_dim_in_light(self) -> None:
        terminal = Variant("medium", "mix", "light").terminal_theme()["terminal"]
        self.assertEqual(terminal["brightBlack"], "#928374")
        self.assertNotEqual(terminal["brightBlack"], terminal["foreground"])
        self.assertEqual(terminal["cursorAccent"], terminal["background"])


if __name__ == "__main__":
    unittest.main()
