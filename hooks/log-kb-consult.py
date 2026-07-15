#!/usr/bin/env python3
"""Log every touch of the knowledge base, so "is it a graveyard?" is a count.

The `knowledge-base` skill names "write-only graveyard" as its first anti-pattern:
the library only self-improves if it's actually consulted. That is precisely the
failure the KB could not detect about itself -- nothing recorded a consult, so a
KB working daily and a KB ignored for six months looked identical.

This runs as a PostToolUse hook, which means the HARNESS runs it, not the model.
That distinction is the whole point: a log the model writes has the same failure
as the thing it measures (an agent that forgets to consult also forgets to log).
Being harness-executed makes it an observation instead of a self-report.

Only a CONSULT counts, and a consult must say so. The command carries a
`# CONSULT` marker (see the knowledge-base skill's CONSULT protocol, step 1);
everything else that touches the KB -- dedupe greps, slug assignment, parity
checks, edits to the skill itself -- logs as `other` and is never counted.

That asymmetry is deliberate. Counting every file touch made the log drift
toward "looks alive", and a false green stops you looking -- exactly the
graveyard it was built to catch. Requiring a positive marker inverts it: a
consult that forgets its marker is *under*counted, the log reads dead, and you
go look. Same discipline problem, opposite blast radius.

Reads stdin JSON: {"tool_name": ..., "tool_input": {...}}
Appends TSV to ~/.claude/knowledge/CONSULT-LOG.tsv: when, kind, tool, what.

Always exits 0. A logger must never break a session -- the measurement is not
worth more than the work it measures.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

LOG = os.path.expanduser("~/.claude/knowledge/CONSULT-LOG.tsv")

# The one positive signal. Only a command that declares itself a consult counts;
# nothing infers intent from the command's shape, because every heuristic I tried
# failed toward "consult" -- the unsafe direction.
#
# Anchored to end-of-line: the marker must be a real trailing comment on the
# command, not merely present in it. Unanchored, anything that *mentions* the
# marker counted as one -- a commit message describing the feature, a grep for
# the marker in the skill file, even the bookkeeping command annotated "no
# # CONSULT marker here". Naming the thing is not doing the thing.
CONSULT = re.compile(r"#\s*CONSULT\s*$", re.I | re.M)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool = str(payload.get("tool_name", ""))
    ti = payload.get("tool_input") or {}
    if not isinstance(ti, dict):
        return 0

    # Only look at path/command fields -- never the whole blob. Otherwise a Grep
    # whose *pattern* is "KNOWLEDGE" would log itself as a consult.
    what = str(ti.get("file_path") or ti.get("path") or ti.get("command") or "")
    if "KNOWLEDGE-" not in what:
        return 0

    # `other` rows are kept, not dropped: they're worth eyeballing, and seeing a
    # pile of them next to zero consults is itself the diagnosis.
    kind = "consult" if CONSULT.search(what) else "other"

    when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    what = what.replace("\t", " ").replace("\n", " ")[:160]

    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{when}\t{kind}\t{tool}\t{what}\n")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
