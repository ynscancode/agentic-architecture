#!/usr/bin/env python3
"""Prove the consistency checker actually catches each divergence class.

A check that has only ever passed is untested -- it may be passing because it
detects nothing. Each case below injects one real divergence into a throwaway
copy of the repo and asserts the checker fails loudly, with a message that
names the problem. Case 0 asserts the pristine tree passes, so we know the
failures are caused by the injected fault and not by a checker that always
fails.

Run:  python tools/test_check_consistency.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(tree: Path) -> tuple[int, str]:
    p = subprocess.run(
        [sys.executable, str(tree / "tools" / "check_consistency.py")],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return p.returncode, p.stdout + p.stderr


def sub(path: Path, old: str, new: str) -> None:
    t = path.read_text(encoding="utf-8")
    if old not in t:
        raise AssertionError(f"fixture drifted: {old!r} not found in {path.name}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")


def rename_role(path: Path, old: str, new: str) -> None:
    """Rename EVERY whole-word occurrence of a role. Renaming just the first is
    not a real rename -- the role is still there, and a check that looks for the
    role anywhere in the file would rightly still find it."""
    t = path.read_text(encoding="utf-8")
    t2, n = re.subn(rf"(?<![a-z0-9-]){re.escape(old)}(?![a-z0-9-])", new, t)
    if n == 0:
        raise AssertionError(f"fixture drifted: no whole-word {old!r} in {path.name}")
    path.write_text(t2, encoding="utf-8")


# Each case: (name, mutate_fn, expected substring in the failure report)
CASES = [
    (
        "frontmatter name != filename",
        lambda t: sub(t / "agents" / "dba.md", "name: dba", "name: database-admin"),
        "frontmatter name `database-admin` != filename `dba`",
    ),
    (
        "pointer to a skill that doesn't exist",
        lambda t: sub(t / "agents" / "engineering-director.md",
                      "`team-communication` skill", "`team-comms` skill"),
        "points at `team-comms` skill, which does not exist",
    ),
    (
        "pointer to a section that was renamed",
        lambda t: sub(t / "skills" / "team-communication" / "SKILL.md",
                      "## Board maintenance", "## Archiving the board"),
        'points at "Board maintenance" in the `team-communication` skill',
    ),
    (
        "roster names an agent with no file",
        lambda t: (t / "agents" / "dba.md").unlink(),
        "roster lists `dba`, but agents/dba.md does not exist",
    ),
    (
        "agent file missing from the roster",
        lambda t: shutil.copy(t / "agents" / "dba.md", t / "agents" / "data-scientist.md"),
        "agents/data-scientist.md exists but is not in the director's roster",
    ),
    (
        "agent missing from the routing tree",
        lambda t: rename_role(t / "skills" / "team-orchestration" / "SKILL.md", "dba", "dbadmin"),
        "is a real agent but never appears in the hierarchy/routing tree",
    ),
    (
        "restated spec creeps back into a prompt",
        lambda t: sub(t / "agents" / "engineering-director.md",
                      "## How you operate",
                      "## How you operate\n\nShards are capped at 10,000 lines."),
        "restates the shard line cap",
    ),
    (
        "restated marker format creeps back into a prompt",
        lambda t: sub(t / "agents" / "engineering-director.md",
                      "## How you operate",
                      "## How you operate\n\nWrap it in ARCH-NNNN:START and ARCH-NNNN:END."),
        "restates the board archive boundary-marker format",
    ),
    (
        "bracketed boundary marker (the historical bug)",
        lambda t: sub(t / "skills" / "team-communication" / "SKILL.md",
                      "<!-- ARCH-NNNN:START -->", "<!-- [ARCH-NNNN]:START -->"),
        "boundary marker contains a bracket",
    ),
]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        pristine = Path(tmp) / "pristine"
        shutil.copytree(ROOT, pristine, ignore=shutil.ignore_patterns(".git"))

        # Case 0: the pristine tree must PASS, or every failure below is meaningless.
        code, out = run(pristine)
        if code != 0:
            print("FAIL  pristine tree does not pass -- fix that first:\n" + out, file=sys.stderr)
            return 1
        print("  ok    pristine tree passes")

        bad = 0
        for name, mutate, expect in CASES:
            tree = Path(tmp) / re.sub(r"\W+", "_", name)
            shutil.copytree(pristine, tree)
            mutate(tree)
            code, out = run(tree)
            if code == 0:
                print(f"  FAIL  {name}\n        checker did not notice", file=sys.stderr)
                bad += 1
            elif expect not in out:
                print(f"  FAIL  {name}\n        caught, but message was unexpected."
                      f"\n        want: {expect}\n        got:  {out.strip()[:300]}", file=sys.stderr)
                bad += 1
            else:
                print(f"  ok    caught: {name}")

    if bad:
        print(f"\n{bad}/{len(CASES)} divergence(s) NOT caught\n", file=sys.stderr)
        return 1
    print(f"\n  all {len(CASES)} divergence classes caught\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
