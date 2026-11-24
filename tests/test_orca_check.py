import unittest

from gruvbox_orca.orca_check import complete, dropped_tokens, monaco_problems

BASE = {"--background": "#282828", "--foreground": "#e2cca9"}


class DroppedTokensTest(unittest.TestCase):
    def test_readable_theme_keeps_everything(self) -> None:
        self.assertEqual(dropped_tokens({**BASE, "--muted-foreground": "#bbaa90"}, "dark"), [])

    def test_failing_text_pair_drops_both_tokens(self) -> None:
        # Orca's own check, run on this theme, drops --background together with the text.
        dropped = dropped_tokens({**BASE, "--muted-foreground": "#555555"}, "dark")
        self.assertIn("--muted-foreground", dropped)
        self.assertIn("--background", dropped)

    def test_git_decoration_uses_the_non_text_floor_and_drops_only_itself(self) -> None:
        theme = {**BASE, "--sidebar": "#282828", "--git-decoration-ignored": "#5a524c"}
        self.assertEqual(dropped_tokens(theme, "dark"), ["--git-decoration-ignored"])
        theme["--git-decoration-ignored"] = "#928374"
        self.assertEqual(dropped_tokens(theme, "dark"), [])

    def test_ring_needs_two_to_one_against_its_surface(self) -> None:
        dropped = dropped_tokens({**BASE, "--ring": "#2c2c2c"}, "dark")
        self.assertEqual(sorted(dropped), ["--ring", "--sidebar-ring", "--worktree-sidebar-ring"])

    def test_translucent_selection_is_composited_over_the_editor(self) -> None:
        self.assertEqual(dropped_tokens({**BASE, "--editor-selection": "#e2cca926"}, "dark"), [])
        self.assertEqual(dropped_tokens({**BASE, "--editor-selection": "#e2cca9cc"}, "dark"), ["--editor-selection"])

    def test_completion_derives_omitted_tokens_like_orca(self) -> None:
        tokens = complete(BASE)
        self.assertEqual(tokens["--card"], "#282828")
        self.assertEqual(tokens["--sidebar"], "#373532")


class MonacoProblemsTest(unittest.TestCase):
    def test_syntax_color_under_three_to_one_is_reported(self) -> None:
        problems = monaco_problems(BASE, "dark", ["#3c3836", "#b0b846"])
        self.assertEqual(len(problems), 1)
        self.assertIn("#3c3836", problems[0])


if __name__ == "__main__":
    unittest.main()
