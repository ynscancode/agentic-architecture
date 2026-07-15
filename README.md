# Agentic Architecture

A complete, working **14-role AI dev team** for [Claude Code](https://claude.com/claude-code) — plus the two systems that keep it from drowning in its own output: a **self-compressing knowledge base** and a **three-tier team-board archive**.

This is not a prompt collection. It's an org chart with escalation rules, a mesh communication layer, and a memory system that gets *denser* as it grows instead of just bigger.

```
                        engineering-director
                       /          |          \
              product-owner  project-manager  tech-lead
                                                  |
        ------------------------------------------------------------------
        |               |            |              |                  |
 senior-frontend  senior-backend    dba    security-engineer   devops-engineer
        |               |
 junior-frontend  junior-backend

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

The load-bearing skills are `team-orchestration` (hierarchy + routing tree), `team-communication` (mesh layer + archive protocol), `knowledge-base` (the cognitive library), and `confidence-check` (a self-verification gate every role runs before reporting done). The other 15 are per-role craft skills.

---

## The two-tier knowledge base

A cross-project library of **generalizable** lessons at `~/.claude/knowledge/`. Universal, not scoped to a repo.

- **Index** (`KNOWLEDGE-INDEX.md`) — one row per lesson: slug, category, shard, status, compressed principle, trigger, tags. Always queried first.
- **Shards** (`KNOWLEDGE-NNN.md`) — the full write-up, 10,000-line cap each, extracted by marker.

**Inclusion is strict — a lesson must be all four:** transferable to a *different* project, non-obvious, actionable, and durable. The litmus: *"Would this help on an unrelated project six months from now?"* If no, it's project memory, not knowledge. Most candidates fail, which is the point — precision over volume.

### It compresses instead of accumulating

When a category reaches **5 active lessons**, a consolidation pass fires automatically (checked on every write, so it can't quietly not happen). Overlapping lessons collapse into one higher-order principle; the originals are marked `superseded-by-KB-XXXX` rather than deleted, so provenance survives the compression. Retrieval skips superseded rows, so the *active* surface stays small even as history grows.

### It records when it's wrong

The part most systems skip. If you retrieve a lesson, apply it, and it turns out wrong or inapplicable — you file a **misfire receipt** on the lesson itself, and raise `Status: active ⚠N` on its index row. Now the next retrieval can't reach the lesson without seeing the warning.

**Deliberately asymmetric: receipts are filed only for failures, never for correct retrievals** — logging successes is noise. Two failure modes, two remediations: an *inapplicable* lesson gets its `Trigger` sharpened with an explicit anti-trigger; a *wrong* one gets corrected, or `deprecated` if unsalvageable.

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

---

## Design principles worth stealing

Even if you never run this, these are the ideas doing the work:

**Never index a mutable file by line number.** Any edit *above* a stored position silently invalidates every number below it — and a stale line number still resolves to *some* content, just the wrong content. Both archives wrap sections in `<!-- SLUG:START -->` / `<!-- SLUG:END -->` markers and extract by pattern range. No line numbers are stored anywhere.

**When the retriever is an LLM, don't reinvent classical IR.** Both indexes use deterministic `grep` for recall, then the model's own judgment over one-sentence summaries for precision. No TF-IDF (statistically meaningless on a small corpus, blind to meaning on any), no fuzzy matching (edit distance, not semantics), no hand-weighted hybrid scores. Embeddings are the *documented* escalation — but only once a category outgrows a single read, and never before.

**Verify before you wipe the source.** Archiving cross-checks that the index's slug set exactly equals the shards' marker set, and resets the live board *only* if they match. A malformed archive write should never cost you the only copy.

**Slugs are permanent.** Never reused, never renumbered, so cross-references keep resolving forever.

**Make triggers fire on the work, not on a feeling.** Lessons are recalled when you touch a *kind of code* (dates, auth, migrations, layout), not when you consciously decide you're "making a design decision" — a decision-shaped trigger under-fires and leaves the library unread. The consolidation check runs on every write for the same reason: a "periodic" pass nothing schedules is a pass that never happens.

**Don't let it become process theater.** The routing tree exists to deploy the *minimum* set of roles that covers the work. A one-line fix by one role beats a five-agent pipeline. Maximal team utilization is a failure mode, not a goal.

---

## Install

Everything is user-level, so it works in **any** project once installed.

```bash
git clone https://github.com/ynscancode/agentic-architecture.git
cd agentic-architecture

cp -r agents/*   ~/.claude/agents/
cp -r skills/*   ~/.claude/skills/
cp -r knowledge/ ~/.claude/knowledge/
```

Then merge `CLAUDE.md.template` into `~/.claude/CLAUDE.md`. It's shipped as `.template` on purpose — dropping a live `CLAUDE.md` at this repo's root would make Claude Code read it as instructions while you work *on* the repo.

> **Merge, don't overwrite,** if you already have a `~/.claude/CLAUDE.md`. It's the wiring: it's what makes the knowledge base get consulted and the director get delegated to. Without it the agents and skills are installed but largely inert.

Nothing else is needed. The per-project files (`TEAM-BOARD.md`, its index, its shards) create themselves on first use, and `knowledge/KNOWLEDGE-INDEX.md` starts empty — the first lesson your sessions record creates `KNOWLEDGE-001.md` at `KB-0001`.

## Verify

```
/agents          # engineering-director + 14 roles
/skills          # 19 skills
```

Then hand Claude something real and multi-disciplinary. You should see it route through `engineering-director`, dispatch specialists in dependency order, and gate on QA/security before reporting done.

---

## License

MIT — see [LICENSE](LICENSE).
