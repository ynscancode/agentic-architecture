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

# Writes to the KB are RECORD, not CONSULT. Counting them as consults would
# inflate the number with the KB's own bookkeeping and hide the exact graveyard
# this exists to catch -- a false positive is the costly direction here.
WRITE_ISH = re.compile(r">>?\s*\S*KNOWLEDGE-|^\s*(cat|tee|cp|mv|printf|echo)\b")


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

    if tool in ("Read", "Grep", "Glob"):
        kind = "read"
    elif WRITE_ISH.search(what):
        kind = "write"
    else:
        kind = "read"  # sed/grep/head/wc against a KNOWLEDGE file

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
