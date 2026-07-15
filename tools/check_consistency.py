#!/usr/bin/env python3
"""Fail loudly when the agent prompts and the skills drift apart.

KB-0008: a spec restated in two authorities drifts silently, because nothing
cross-checks them and both look authoritative. The remedy applied to this repo
is that skills are canonical and agent prompts point at them. That remedy has
two failure modes, and this script exists to make both of them loud:

  1. A pointer dangles. Renaming a skill or a section silently breaks every
     prompt that points at it -- there is no error, the agent just follows an
     instruction to read something that isn't there.
  2. A restatement creeps back in. Someone helpfully re-inlines a spec into a
     prompt "for convenience", and now there are two copies again.

Run:  python tools/check_consistency.py
Exit: 0 = consistent, 1 = divergence found (details on stderr).

SCOPE / KNOWN LIMITATION -- stated plainly rather than implied:
README.md is NOT checked for restatement. A README's job is to describe the
system, so a pointer-only README would be useless. Per KB-0008's own tiebreaker
the load-bearing copy is the one an executable step consumes, and nothing
consumes the README at runtime -- a drifted README misleads a human reader,
which is bad but is not the silent agent-level failure this guards. The README
is therefore knowingly out of scope, not accidentally uncovered.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "agents"
SKILLS = ROOT / "skills"
DIRECTOR = AGENTS / "engineering-director.md"
ORCHESTRATION = SKILLS / "team-orchestration" / "SKILL.md"

failures: list[str] = []


def fail(where: str, msg: str, fix: str) -> None:
    failures.append(f"{where}\n    problem: {msg}\n    fix:     {fix}")


def frontmatter_name(path: Path) -> str | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    m2 = re.search(r"^name:\s*(\S+)\s*$", m.group(1), re.M)
    return m2.group(1) if m2 else None


# ---------------------------------------------------------------- check 1
def check_frontmatter() -> None:
    """An agent's declared name and its filename are two authorities for its
    identity. If they disagree, dispatching it by the name in the roster fails."""
    for f in sorted(AGENTS.glob("*.md")):
        name = frontmatter_name(f)
        if name is None:
            fail(f"agents/{f.name}", "no `name:` in frontmatter", "add a frontmatter `name:` field")
        elif name != f.stem:
            fail(f"agents/{f.name}", f"frontmatter name `{name}` != filename `{f.stem}`",
                 f"rename the file to {name}.md, or set name: {f.stem}")

    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        sf = d / "SKILL.md"
        if not sf.exists():
            fail(f"skills/{d.name}/", "no SKILL.md", "add SKILL.md, or remove the directory")
            continue
        name = frontmatter_name(sf)
        if name is None:
            fail(f"skills/{d.name}/SKILL.md", "no `name:` in frontmatter", "add a frontmatter `name:` field")
        elif name != d.name:
            fail(f"skills/{d.name}/SKILL.md", f"frontmatter name `{name}` != directory `{d.name}`",
                 f"rename the directory to {name}/, or set name: {d.name}")


# ---------------------------------------------------------------- check 2+3
SKILL_REF = re.compile(r"`([a-z][a-z0-9-]*)`\s+skill")
SECTION_REF = re.compile(r'"([^"]+)"\s+(?:section|workflow)')


def check_pointers() -> None:
    """Every `x` skill reference must resolve to skills/x/SKILL.md, and every
    quoted "Y" section/workflow reference must resolve to a real `## Y...`
    heading in the most recently named skill. This is the check that makes the
    pointer-instead-of-restatement design safe: without it, a rename breaks the
    pointer silently and the prompt sends the agent to read nothing."""
    known = {d.name for d in SKILLS.iterdir() if d.is_dir()}
    headings: dict[str, list[str]] = {}
    for s in known:
        text = (SKILLS / s / "SKILL.md").read_text(encoding="utf-8")
        headings[s] = re.findall(r"^##\s+(.*?)\s*$", text, re.M)

    for f in sorted(list(AGENTS.glob("*.md")) + list(SKILLS.glob("*/SKILL.md"))):
        rel = f.relative_to(ROOT).as_posix()
        last_skill: str | None = None
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            # Walk both kinds of reference in POSITIONAL order. A line often
            # names several skills ("...the `team-communication` skill's "Board
            # maintenance" workflow ... per the `knowledge-base` skill's..."),
            # so a quoted section binds to the skill named most recently BEFORE
            # it -- not to the last one on the line.
            refs = sorted(
                [(m.start(), "skill", m) for m in SKILL_REF.finditer(line)]
                + [(m.start(), "section", m) for m in SECTION_REF.finditer(line)]
            )
            for _, kind, ref in refs:
                if kind == "skill":
                    s = ref.group(1)
                    if s not in known:
                        fail(f"{rel}:{i}", f"points at `{s}` skill, which does not exist",
                             f"create skills/{s}/SKILL.md, or fix the reference")
                    else:
                        last_skill = s
                    continue

                want = ref.group(1)
                if last_skill is None:
                    continue  # a quoted phrase with no skill named yet: not a pointer
                # References use a prefix of the heading, since headings carry
                # parenthetical qualifiers -- "Board maintenance" points at
                # "## Board maintenance (archiving -- engineering-director only)".
                if not any(h == want or h.startswith(want) for h in headings[last_skill]):
                    fail(f"{rel}:{i}",
                         f'points at "{want}" in the `{last_skill}` skill, which has no such section',
                         f"add a `## {want}` heading to skills/{last_skill}/SKILL.md, "
                         f"or update the pointer. Existing: {headings[last_skill]}")


# ---------------------------------------------------------------- check 4
def check_roster() -> None:
    """The team roster exists in three places: agents/*.md (the real files), the
    director's dispatch list, and team-orchestration's hierarchy. A role in the
    director's list with no file means dispatching it fails at runtime; a file
    missing from the routing tree means a role nobody can be routed to."""
    files = {f.stem for f in AGENTS.glob("*.md")} - {"engineering-director"}

    text = DIRECTOR.read_text(encoding="utf-8").splitlines()
    listed: set[str] = set()
    seen_header = False
    for line in text:
        if line.startswith("The team you command"):
            seen_header = True
            continue
        if seen_header:
            if line.startswith("- "):
                listed.update(re.findall(r"`([a-z][a-z0-9-]*)`", line))
            elif line.strip() == "" and listed:
                break

    if not listed:
        fail("agents/engineering-director.md",
             "could not find the roster (no `- ` list after 'The team you command')",
             "keep the roster as a `- ` bulleted list of backticked names under that header")

    for missing in sorted(listed - files):
        fail("agents/engineering-director.md",
             f"roster lists `{missing}`, but agents/{missing}.md does not exist",
             f"create agents/{missing}.md, or drop it from the roster")
    for extra in sorted(files - listed):
        fail("agents/engineering-director.md",
             f"agents/{extra}.md exists but is not in the director's roster",
             f"add `{extra}` to the roster, or delete the agent")

    orch = ORCHESTRATION.read_text(encoding="utf-8")
    for role in sorted(files):
        if not re.search(rf"(?<![a-z0-9-]){re.escape(role)}(?![a-z0-9-])", orch):
            fail("skills/team-orchestration/SKILL.md",
                 f"`{role}` is a real agent but never appears in the hierarchy/routing tree",
                 f"add {role} to the hierarchy and routing tree, or delete the agent")


# ---------------------------------------------------------------- check 5
# Spec tokens the skills own. Each must not reappear in an agent prompt --
# that is a restatement, and restatements are what KB-0008 says will drift.
# (pattern, human name, owning skill)
CANONICAL_TOKENS: list[tuple[str, str, str]] = [
    (r"10,000", "the shard line cap", "team-communication / knowledge-base"),
    (r"ARCH-[N0-9]{4}:(?:START|END)", "the board archive boundary-marker format", "team-communication"),
    (r"KB-[N0-9]{4}:(?:START|END)", "the knowledge-base boundary-marker format", "knowledge-base"),
    (r"ROLE-YYYYMMDDTHHMMSS", "the board entry ID format", "team-communication"),
    (r"###\s*\[ROLE-", "the board entry heading format", "team-communication"),
    (r"superseded-by-KB-", "the superseded Status format", "knowledge-base"),
    (r"sed\s+-n", "the marker-extraction command", "team-communication / knowledge-base"),
    (r"Slug\s*\|\s*Category\s*\|\s*Shard", "the index column layout", "knowledge-base"),
    (r"max existing", "the slug-assignment rule", "team-communication / knowledge-base"),
]


def check_no_restatement() -> None:
    for f in sorted(AGENTS.glob("*.md")):
        rel = f"agents/{f.name}"
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for pat, what, owner in CANONICAL_TOKENS:
                if re.search(pat, line):
                    fail(f"{rel}:{i}",
                         f"restates {what}, which the {owner} skill owns",
                         "replace the restatement with a pointer to the skill -- "
                         "two copies of a spec drift silently (KB-0008)")


# ---------------------------------------------------------------- check 6
BRACKETED_MARKER = re.compile(r"<!--\s*\[")


def check_markers() -> None:
    """The historical bug: a prompt specified `<!-- [ARCH-0001]:START -->` while
    the skill's sed retrieval matches the unbracketed form, so the extraction
    silently found nothing. Brackets belong in the `# [ARCH-0001]` heading only,
    never inside a boundary marker."""
    for f in sorted(ROOT.rglob("*.md")):
        if ".git" in f.parts:
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if BRACKETED_MARKER.search(line):
                fail(f"{f.relative_to(ROOT).as_posix()}:{i}",
                     "boundary marker contains a bracket",
                     "markers are unbracketed (`<!-- ARCH-0001:START -->`); the "
                     "sed retrieval will silently fail to match a bracketed one")


def main() -> int:
    # Skills and prompts are full of em-dashes; a cp1252 console would mangle
    # or crash on them. Force UTF-8 so the report is readable everywhere.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    for check in (check_frontmatter, check_pointers, check_roster,
                  check_no_restatement, check_markers):
        check()

    if failures:
        print(f"\n  DIVERGENCE: {len(failures)} problem(s) found\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}\n", file=sys.stderr)
        print("  The skills are canonical. Prompts point at them; they do not "
              "restate them.\n", file=sys.stderr)
        return 1

    print("  consistent: pointers resolve, roster agrees, no restatements, markers clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
