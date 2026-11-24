"""Writes every variant's app and terminal theme and the manifest entries, or checks them."""

import argparse
import json
import sys
from pathlib import Path

from gruvbox_orca.themes import Variant, problems, variants

ROOT = Path(__file__).resolve().parents[2]
GENERATED_DIRS = ("themes", "terminal")


def dump(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def outputs(root: Path, built: list[tuple[Variant, dict]]) -> dict[Path, str]:
    files: dict[Path, str] = {}
    themes, terminals = [], []
    for variant, app_theme in built:
        files[root / f"themes/{variant.slug}.json"] = dump(app_theme)
        files[root / f"terminal/{variant.slug}.json"] = dump(variant.terminal_theme())
        themes.append({"id": variant.slug, "title": variant.title, "path": f"themes/{variant.slug}.json"})
        terminals.append({"id": variant.slug, "title": variant.title, "path": f"terminal/{variant.slug}.json"})
    manifest_path = root / "orca-plugin.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["contributes"] = {"themes": themes, "terminalThemes": terminals}
    files[manifest_path] = dump(manifest)
    return files


def stale_files(root: Path, files: dict[Path, str]) -> set[Path]:
    on_disk = {p for d in GENERATED_DIRS for p in (root / d).glob("*.json")}
    return on_disk - files.keys()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gruvbox-orca", description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if a generated file differs from the committed one")
    mode.add_argument("--report", action="store_true", help="print each variant's contrast adjustments")
    args = parser.parse_args(argv)

    built = [(v, v.app_theme()) for v in variants()]
    failures = [f"{v.slug}: {problem}" for v, theme in built for problem in problems(theme)]
    for failure in failures:
        print(failure, file=sys.stderr)
    if args.report:
        for v, _ in built:
            print(f"{v.slug}: {'; '.join(v.adjustments) or 'no adjustments'}")
        return 1 if failures else 0
    if failures:
        return 1

    files = outputs(ROOT, built)
    stale = stale_files(ROOT, files)
    if args.check:
        drift = sorted(p for p, text in files.items() if not p.exists() or p.read_text() != text) + sorted(stale)
        for p in drift:
            print(f"out of date: {p.relative_to(ROOT)} (run `mise run generate`)", file=sys.stderr)
        return 1 if drift else 0

    for d in GENERATED_DIRS:
        (ROOT / d).mkdir(exist_ok=True)
    for p, text in files.items():
        p.write_text(text)
    for p in stale:
        p.unlink()
    print(f"wrote {len(files)} files, removed {len(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
