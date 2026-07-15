# Agentic Architecture

A complete, working **14-role AI dev team** for [Claude Code](https://claude.com/claude-code) — plus the two systems that keep it from drowning in its own output: a **self-compressing knowledge base** and a **three-tier team-board archive**.

This is not a prompt collection. It's an org chart with escalation rules, a mesh communication layer, and a memory system that gets *denser* as it grows instead of just bigger.

```
                          engineering-director
                         /          |          \
                product-owner  project-manager  tech-lead
                                                    |
        ----------------------------------------------------------------
        |                    |          |             |               |
 senior-frontend-dev  senior-backend-dev  dba  security-engineer  devops-engineer
        |                    |
 junior-frontend-dev  junior-backend-dev

  ui-ux-designer            -> feeds specs into the frontend devs
  qa-engineer               -> verifies any implementation role
  technical-writer          -> documents shipped work
  code-refactoring-engineer -> cleans up after QA confirms behavior
```

---

## The problem this solves

Multi-agent setups fail in three predictable ways. Each subsystem here targets one:

| Failure | What actually goes wrong | The answer |
|---|---|---|
| **Everything routed through one orchestrator** | Agents don't share memory, so every cross-role finding has to be relayed by hand. Things get dropped. | **Mesh layer** — a shared `TEAM-BOARD.md` every role reads and appends to directly. |
| **Shared state grows without bound** | The board becomes a multi-thousand-line file that every dispatched agent must read before starting. | **Three-tier archive** — live board stays small; history stays greppable, out of the default read path. |
| **The same mistake, re-derived forever** | Nothing survives the session. Lessons evaporate. | **Two-tier knowledge base** — cross-project, consulted before work, compressed as it grows. |

---

## What's in here

| | |
|---|---|
| `agents/` | 15 subagent definitions — `engineering-director` plus the 14 roles it commands |
| `skills/` | 19 skills — the protocols the agents execute |
| `knowledge/` | The knowledge-base index, shipped as an empty scaffold |
| `CLAUDE.md.template` | Global instructions that wire it all together |
| `tools/` | The consistency checker and its self-test (see [Keeping it consistent](#keeping-it-consistent)) |
| `hooks/` | A `PostToolUse` hook that logs KB consults, so "is it a graveyard?" is a count |

The load-bearing skills are `team-orchestration` (hierarchy + routing tree), `team-communication` (mesh layer + archive protocol), `knowledge-base` (the cognitive library), and `confidence-check` (a self-verification gate every role runs before reporting done). The other 15 are per-role craft skills.

---

## The two-tier knowledge base

A cross-project library of **generalizable** lessons at `~/.claude/knowledge/`. Universal, not scoped to a repo.

- **Index** (`KNOWLEDGE-INDEX.md`) — one row per lesson: slug, category, shard, status, compressed principle, trigger, tags. Always queried first.
- **Shards** (`KNOWLEDGE-NNN.md`) — the full write-up, 10,000-line cap each, extracted by marker.

```mermaid
flowchart TB
    LES["A lesson from a<br/>resolved problem"] --> TEST{"The 4-part test<br/>transferable · non-obvious<br/>actionable · durable"}
    TEST -->|"fails — most do"| MEM["Project memory<br/>(or nothing)"]

    subgraph STORE["Two-tier store · ~/.claude/knowledge/ · portable across every project"]
        direction TB
        IDX["<b>TIER 1 — KNOWLEDGE-INDEX.md</b><br/>one row per lesson<br/>Slug · Category · Shard · Status · Principle · Trigger · Tags<br/><i>compressed · always queried first</i>"]
        SHARD["<b>TIER 2 — KNOWLEDGE-NNN.md</b><br/>the full write-up, bracketed by START / END markers<br/><i>cold · 10,000-line cap, then rotate · never scanned to find things</i>"]
        IDX -->|"the row names its shard;<br/>sed the markers to pull just that lesson"| SHARD
    end

    TEST -->|"passes — RECORD<br/>writes both tiers"| STORE
    STORE --> CONSULT["<b>CONSULT</b><br/>1 · grep the index by keyword or Category<br/>2 · read the candidates' Trigger + Principle<br/>3 · heed Status — active · ⚠N · superseded · deprecated"]
    CONSULT --> APPLY["Apply the Principle"]
    APPLY -->|"it was wrong or<br/>inapplicable here"| MIS["<b>MISFIRE</b> — append a receipt to the lesson,<br/>raise its Status to active ⚠N<br/><i>failures only; logging successes is noise</i>"]
    MIS --> STORE
    STORE --> TRIG{"5+ lessons added to one Category<br/>since that category's last pass?"}
    TRIG -->|"yes"| CONS["<b>CONSOLIDATE</b> — merge the overlaps into one<br/>higher-order principle. Subsumed rows become<br/>superseded-by-KB-XXXX — never deleted.<br/><i>Record the watermark even if nothing merged</i>"]
    CONS --> STORE
```

**Inclusion is strict — a lesson must be all four:** transferable to a *different* project, non-obvious, actionable, and durable. The litmus: *"Would this help on an unrelated project six months from now?"* If no, it's project memory, not knowledge. Most candidates fail, which is the point — precision over volume.

### It compresses instead of accumulating

When **5 lessons have been added to a category since that category's last consolidation pass**, a compression pass fires automatically (checked on every write, so it can't quietly not happen). Overlapping lessons collapse into one higher-order principle; the originals are marked `superseded-by-KB-XXXX` rather than deleted, so provenance survives the compression. Retrieval skips superseded rows, so the *active* surface stays small even as history grows.

The trigger measures **new material, not standing inventory** — and that distinction is load-bearing. It counts a category *label*, so it can't see whether the content actually overlaps; it's a proxy for "there might be redundancy here." When a category's lessons turn out genuinely distinct, the pass merges nothing and supersedes nothing, so a total-count trigger would stay armed and re-fire a fruitless pass on *every* subsequent write to that category, forever. Each pass records a watermark instead — including a pass that merges nothing, since "these are distinct" is a result — so every batch of new material gets evaluated exactly once.

### It records when it's wrong

The part most systems skip. If you retrieve a lesson, apply it, and it turns out wrong or inapplicable — you file a **misfire receipt** on the lesson itself, and raise `Status: active ⚠N` on its index row. Now the next retrieval can't reach the lesson without seeing the warning.

**Deliberately asymmetric: receipts are filed only for failures, never for correct retrievals** — logging successes is noise. Two failure modes, two remediations: an *inapplicable* lesson gets its `Trigger` sharpened with an explicit anti-trigger; a *wrong* one gets corrected, or `deprecated` if unsalvageable.

### It knows if it's being ignored

The first anti-pattern this library names is the **write-only graveyard**: it only self-improves if it's actually consulted. That's a failure you can't notice by feel — a consult that never happens leaves no trace and costs you nothing you can perceive, so a KB working daily and one ignored for months look identical from the outside.

So a `PostToolUse` hook logs every read of the KB to `CONSULT-LOG.tsv`. **The harness writes it, not the model** — which is the whole point. A log the agent maintained would share the exact failure it measures, since an agent that forgets to consult also forgets to log. Writes are classified separately from reads, so the KB's own bookkeeping can't inflate the number and hide the graveyard.

It's checked at RECORD time, never on a calendar — a check scheduled by nothing is a check that never runs. And it's a smoke detector, not a dashboard: the only actionable signal is ≈0 reads across several records, which means the triggers aren't firing, the categories don't match your work, or the wiring is broken.

### One curator

The top-level session owns all writes. Subagents **propose** lessons in their reports; they never write. This is policy, not a sandbox barrier — a subagent *can* write to `~/.claude/`. Two reasons it holds anyway: there's no file locking (concurrent writes to the index would silently lose rows), and the inclusion test needs a whole-session view that a subagent working one batch doesn't have.

---

## The three-tier team board

`TEAM-BOARD.md` at the project root is the mesh layer: every role reads it before starting and appends findings relevant to other roles as they work. Entries are strictly formatted — `### [ROLE-timestamp]` plus five required fields — because a freeform note can't be machine-checked as resolved, which means it can't be cleanly archived.

**Mesh visibility is not decision authority.** Seeing another role's entry doesn't mean acting on it outside your remit. Conflicting entries are an escalation signal, not a race to whoever gets there first.

Left alone, an append-only board becomes the exact context-bloat problem it was meant to solve. So the `engineering-director` — and only the director — prunes it:

- **Live board** — `TEAM-BOARD.md`: active work only.
- **Master index** — `TEAM-BOARD-INDEX.md`: one row per archived batch. The registry the director queries first.
- **Shards** — `TEAM-BOARD-ARCHIVE-NNN.md`: cold storage, full text, 10,000-line cap.

Nothing is ever deleted — it moves out of every future agent's default read while staying greppable. All three files are per-project and created lazily: the live board on first touch, the index and shards on first archive.

```mermaid
flowchart TB
    ROLES["<b>Any of the 14 roles</b> — append-only<br/>read the board before starting · post findings other roles need<br/>every entry: ### ROLE-timestamp + 5 required fields<br/><i>scoped Edit of your own Status line only — never another's entry</i>"]
    DIR["<b>engineering-director</b><br/><i>the only role that archives, and the only one that reads the archive</i>"]

    LIVE["<b>TIER 1 — TEAM-BOARD.md</b><br/>the live mesh · ACTIVE WORK ONLY<br/><i>every role reads this before starting</i>"]

    ROLES --> LIVE
    DIR -->|"reads to verify cross-role issues<br/>actually got resolved, not just raised"| LIVE

    LIVE --> DONE{"Every entry in the batch<br/>RESOLVED and well-formed?"}
    DONE -->|"no — still in flight"| LEAVE["Leave it.<br/>Archive only the finished batch"]
    DONE -->|"yes"| ARCH["<b>ARCHIVE</b> — director only<br/>1 · capacity-check the shard; rotate if it would overflow<br/>2 · assign a permanent slug — max across all shards + 1<br/>3 · append the section, wrapped in boundary markers<br/>4 · register one disambiguating row in the index"]

    subgraph COLD["The archive — cold storage, out of every agent's default read"]
        direction TB
        TBI["<b>TIER 2 — TEAM-BOARD-INDEX.md</b><br/>one row per archived batch<br/>Slug · Category · Shard · Heading · Resolution summary · Tags<br/><i>the registry — always queried first</i>"]
        TBA["<b>TIER 3 — TEAM-BOARD-ARCHIVE-NNN.md</b><br/>full section text, bracketed by ARCH-NNNN START / END<br/><i>cold · 10,000-line cap, then rotate · never scanned to find things</i>"]
        TBI -->|"the row names its shard;<br/>sed the markers to pull just that section"| TBA
    end

    ARCH --> COLD
    ARCH --> GATE{"<b>PARITY GATE</b><br/>index slug set == shards' START-marker set?"}
    GATE -->|"no — malformed"| FIX["Fix the archive.<br/><b>Do NOT reset.</b>"]
    GATE -->|"yes"| RESET["Reset TEAM-BOARD.md to the empty template<br/><i>verify before you wipe the source — a bad archive<br/>write must never cost you the only copy</i>"]
    RESET --> LIVE
    DIR -->|"consults it only on a trigger: a request<br/>looks related to already-archived work"| TBI
```

**Why the gate matters:** the reset is the only destructive step in the system. Checking that the archive write landed intact *before* wiping the source is what stops a malformed write from costing you the only copy.

---

## How it fits together

Two stores, two lifetimes. The knowledge base is **installed once and follows you everywhere**; the team board is **created per project and stays there**. That split is the load-bearing idea: a portable principle goes in the KB, a fact about one repo goes in project memory or the board. The litmus is *"would this help on an unrelated project six months from now?"*

```mermaid
flowchart LR
    subgraph USER["USER LEVEL — ~/.claude/ — installed once, follows you to every project"]
        direction TB
        DEFS["<b>agents/</b> · 15 role definitions<br/><b>skills/</b> · 19 protocols<br/><i>canonical — the prompts point here</i>"]
        KB["<b>KNOWLEDGE BASE</b> · 2-tier<br/>KNOWLEDGE-INDEX.md → KNOWLEDGE-NNN.md<br/><b><i>portable principles</i></b>"]
        LOG["<b>CONSULT-LOG.tsv</b><br/><i>written by a harness hook —<br/>not by any agent</i>"]
        KB -->|"every read logged"| LOG
    end

    subgraph TEAM["THE TEAM — spawned per request"]
        direction TB
        TOP["<b>TOP-LEVEL SESSION</b><br/><i>the KB's single curator —<br/>the only thing that writes to it</i>"]
        DIR["<b>engineering-director</b><br/>routes · verifies · archives"]
        SPEC["<b>14 specialist roles</b><br/>PO · PM · tech-lead · devs · dba<br/>QA · security · devops · design · docs"]
        TOP -->|"delegates substantial work"| DIR
        DIR -->|"dispatches in dependency order,<br/>passing any KB Principle verbatim"| SPEC
        SPEC -.->|"propose a lesson"| DIR
        DIR -.->|"propose — never writes"| TOP
    end

    subgraph PROJ["PROJECT LEVEL — one set per repo, created lazily on first use"]
        direction TB
        BOARD["<b>TEAM BOARD</b> · 3-tier<br/>TEAM-BOARD.md → -INDEX.md → -ARCHIVE-NNN.md<br/><b><i>this project's work</i></b>"]
        PMEM["<b>projects/&lt;name&gt;/memory/</b><br/><b><i>this project's facts</i></b>"]
    end

    DEFS ==>|"define"| TEAM
    KB ==>|"CONSULT before<br/>non-trivial work"| TEAM
    TOP ==>|"RECORD"| KB
    LOG -.->|"checked at RECORD time:<br/>is this a graveyard?"| TOP
    SPEC ==>|"append findings"| BOARD
    DIR ==>|"verifies, then archives<br/>the finished batch"| BOARD
    TOP ==> PMEM
```

**Why one curator:** there's no file locking anywhere in this system. Concurrent writes to an index would silently lose rows, and the KB's inclusion test needs a whole-session view that a subagent working one batch doesn't have. Subagents *can* write to `~/.claude/` — this is policy, not a sandbox barrier, so it holds only because it's followed deliberately.

## Install

Everything is user-level, so it works in **any** project once installed.

```bash
git clone https://github.com/ynscancode/agentic-architecture.git
cd agentic-architecture

mkdir -p ~/.claude/agents ~/.claude/skills ~/.claude/knowledge

cp -r agents/* ~/.claude/agents/
cp -r skills/* ~/.claude/skills/
cp -n knowledge/KNOWLEDGE-INDEX.md ~/.claude/knowledge/   # -n: never clobber an existing KB
```

To enable the consult log, also copy the hook and register it:

```bash
mkdir -p ~/.claude/hooks && cp hooks/log-kb-consult.py ~/.claude/hooks/
```

Then merge this into `~/.claude/settings.json` (merge — don't overwrite the file):

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Read|Grep|Glob|Bash",
      "hooks": [{
        "type": "command",
        "command": "python ~/.claude/hooks/log-kb-consult.py 2>/dev/null || true",
        "async": true,
        "timeout": 10
      }]
    }]
  }
}
```

Requires `python` on `PATH`. The hook is optional — everything else works without it; you just won't be able to tell whether the KB is a graveyard.

> **`cp -n` on that last line is load-bearing.** If you already run a knowledge base, plain `cp` would overwrite your `KNOWLEDGE-INDEX.md` with this empty scaffold and orphan every lesson in your shards. `-n` refuses to overwrite. The first two lines *do* overwrite same-named agents and skills — check for collisions first if you have your own.

Then merge `CLAUDE.md.template` into `~/.claude/CLAUDE.md`. It's shipped as `.template` on purpose — dropping a live `CLAUDE.md` at this repo's root would make Claude Code read it as instructions while you work *on* the repo.

> **Merge, don't overwrite,** if you already have a `~/.claude/CLAUDE.md`. It's the wiring: it's what makes the knowledge base get consulted and the director get delegated to. Without it the agents and skills are installed but largely inert.

Nothing else is needed. The per-project files (`TEAM-BOARD.md`, its index, its shards) create themselves on first use, and `knowledge/KNOWLEDGE-INDEX.md` starts empty — the first lesson your sessions record creates `KNOWLEDGE-001.md` at `KB-0001`.

## Verify

```bash
ls ~/.claude/agents/ | wc -l      # 15 — engineering-director + 14 roles
ls -d ~/.claude/skills/*/ | wc -l # 19
```

Run `/agents` in an interactive session to confirm Claude Code actually loaded them.

Then hand Claude something real and multi-disciplinary. You should see it route through `engineering-director`, dispatch specialists in dependency order, and gate on QA/security before reporting done.

---

## Keeping it consistent

The skills are canonical; the agent prompts point at them rather than restating them. That trades one failure mode for another — a restatement drifts silently, and a pointer *dangles* silently when a section gets renamed. `tools/check_consistency.py` guards both directions, and CI runs it on every push and PR:

```bash
python tools/check_consistency.py       # 0 = consistent, 1 = divergence, with file:line
python tools/test_check_consistency.py  # proves the checker still detects all 9 classes
```

It catches dangling skill/section pointers, roster disagreement across the three places the team is named, spec restatements creeping back into a prompt, frontmatter/filename mismatch, and bracketed boundary markers — the last being a real bug this repo shipped with, where a prompt specified a marker format the skill's own `sed` retrieval silently fails to match.

The self-test exists because a check that has only ever passed is untested; a green check that verifies nothing is worse than no check, since it buys false confidence. **This README is deliberately out of the checker's scope** — describing the system is a README's job, so it can't be pointer-only, which means its claims are verified by hand and can go stale between passes.

---

## License

MIT — see [LICENSE](LICENSE).
