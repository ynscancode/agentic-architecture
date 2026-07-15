---
name: team-communication
description: Use whenever your work relates to, depends on, or affects another role's work — check and post to the shared team board file so related agents have visibility without needing everything relayed by the orchestrator. Mesh communication layer for the dev team; use alongside team-orchestration, which still governs decision authority and escalation.
---

# Team Communication (Mesh Layer)

Agents don't share conversation memory, and the Task management tools (`TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate`) are **not available to subagents** — confirmed: they return "exists but is not enabled in this context" when a subagent calls them, even when declared in the agent's tool list. The mesh layer instead uses a plain shared file, which every agent can reach via `Read`/`Write` (tools that are actually available to subagents).

This is **additive** to `team-orchestration`, not a replacement: the orchestrator (`engineering-director` or whoever dispatched you) still controls sequencing and primary handoffs. The mesh layer is for the *side* information — things a related role needs to know but that aren't the main thing being handed off.

## The board file

Location: `<project-root>/TEAM-BOARD.md` — at the project root, alongside `CLAUDE.md`/`README.md`. **Not** inside `.claude/`: that directory holds permissions/hooks/agent definitions and shouldn't carry team state. The project root is the natural home for project state — version-controlled alongside the code, and readable by every role with no special handling.

> **Correction (2026-07-15 probe):** this rule was long justified by the claim that "a subagent `Write` under `.claude/` will be denied at the sandbox level." That claim is **unverified for the project-level `.claude/` and provably false for the user-level `~/.claude/`** — a subagent write there succeeded with no prompt. Keep the board at the project root for the reasons above, not for a sandbox restriction that may not exist. Don't rely on `.claude/` being write-protected anywhere.

**Resolving the path and guaranteeing the file exists — do this every time, no exceptions:**
1. `Glob` for `**/CLAUDE.md` or `**/.git` to find the project root. Use the directory containing the first match as `<project-root>`.
2. If neither Glob turns up anything (no project markers found), fall back to your current working directory as `<project-root>`. Never treat "couldn't locate a project root" as a reason to skip the board.
3. `Read` `<project-root>/TEAM-BOARD.md`.
4. **If `Read` errors because the file doesn't exist, that is not a blocker — it means you create it, immediately, with `Write`:**
   ```
   # Team Board

   Shared mesh-communication log for the dev team. Append-only — see the `team-communication` skill for entry format and rules.

   ---
   ```
   Then proceed exactly as if the board existed and was empty. Do not ask permission, do not report "no team board available," and do not stop the task because of this — an empty/newly-created board is a normal, expected starting state, not an error condition.
5. Whoever hits this situation first (any role, including the orchestrator before its first dispatch) creates it. There is no scenario where the correct response to a missing board is to report it as unavailable rather than creating it.

Entry format — **MANDATORY for every entry. Freeform prose notes are not allowed.** Each entry is a level-3 heading with a unique ID; never edit another agent's entry text, only ever append new entries or update your own entry's status line:

```
### [ROLE-YYYYMMDDTHHMMSS] <short subject>
- **From:** <your role>
- **For:** <role this is relevant to, or "all">
- **Status:** OPEN
- **Detail:** <concrete finding — file/line, what's wrong or relevant, why it matters>
- **Resolution:** _(filled in by whoever resolves it)_
```

- **ID:** `<role-name>-<YYYYMMDDTHHMMSS>` using the **actual current UTC-ish timestamp** (e.g. `qa-engineer-20260715T143200`) so IDs never collide between agents. The `HHMMSS` is required — get it from `date -u +%Y%m%dT%H%M%S` if unsure; do not invent a time or drop the time component.
- **All five fields are required.** `Status` is `OPEN` or `RESOLVED`. `Detail` may span multiple lines/bullets, but every entry must have all five field labels present. A note with nothing to resolve still fills `Resolution:` with `_(informational — no action needed)_`.
- This is what the archiving `**Status:** RESOLVED` check (Board maintenance step 1) reads, and what makes an entry machine-checkable. An entry missing the format can't be verified as done — so it can't be cleanly archived.

## Before starting work

1. **Read the board.** If it exists, read the whole file and look for entries tagged `For:` your role or `all`, especially ones still `OPEN`. Don't re-derive what's already been found.
2. **Don't skip this because the file "is probably empty."** The cost of checking is low; the cost of duplicate or conflicting work is not.

## While working

3. **Append findings relevant to another role as you find them** — don't wait until you're fully done. Read the current file, then `Write` the full file back with your new entry appended at the end, **in the mandatory entry format above** (all five fields, real timestamp ID). Re-read immediately before writing to minimize the race window (see Anti-patterns).
4. **Be concrete.** A mesh entry should be specific enough the receiving agent doesn't need to ask you anything else: file, line, what's wrong, why it matters to them.

## Resolving / updating an entry

5. To mark an entry resolved, use a scoped `Edit` on **that entry only** — change `**Status:** OPEN` → `**Status:** RESOLVED` and fill in the `**Resolution:**` line.
   - **Anchor the match to the entry's ID.** `Edit` needs a *unique* `old_string`, and a bare `- **Status:** OPEN` line is **not** unique on a board with more than one entry. Include the entry's `### [ROLE-timestamp]` heading and the lines between it and the target line in your `old_string`, so the match can only land on your entry. (A single-entry board hides this — don't let that habit carry over.)
   - If `Edit` reports a non-unique match, that's the guard working: widen `old_string` with more of that entry's context. **Do not fall back to a whole-file `Write`** — that's the race-prone path this step exists to avoid.
   - Never touch any other entry while doing this.

## After finishing

6. **Leave an outcome note** — append a final entry (or update your own) stating what you did/decided/what's still open, so any agent picking up related work next has context without the orchestrator manually relaying it.

## Board maintenance (archiving — engineering-director only)

The board is append-only for every other role — which, left unmanaged across every batch of work a project ever does, turns it into a multi-thousand-line file that every dispatched agent has to read before starting anything. `engineering-director` is the sole exception: it owns pruning the board so the rest of the team doesn't have to.

**The archive is three tiers** (all at `<project-root>`, alongside the live board):
- **Live board** — `TEAM-BOARD.md`: active work only.
- **Master index** — `TEAM-BOARD-INDEX.md`: one row per archived section (slug, category, shard, heading, one-sentence resolution summary, tags). The registry the director queries first; it holds *no* full history and *no* line numbers.
- **Shards** — `TEAM-BOARD-ARCHIVE-NNN.md` (zero-padded, `-001`, `-002`, …): cold storage holding the full section text. **Hard cap: 10,000 lines per shard.**

### Bootstrapping the tiers in a new project

This system is portable: the skill and the director are user-level, so they work in **any** project, but the three files are per-project and are created **on first use, lazily**:
- **Live board** — created eagerly, the first time any role resolves the board path (see step 4 of the path-resolution list above). Every project gets one as soon as the team touches it.
- **Index + shards** — created lazily, at the project's **first archive**. A project that never archives never gets them; that's intended (no empty-file clutter).

**When creating either for the first time in a project, use these canonical templates verbatim — do not improvise.** Every project's structure must be identical, or the retrieval protocol (which assumes exact table columns and marker formats) breaks.

**`TEAM-BOARD-INDEX.md` — create with this, then append rows beneath the table header:**

``````markdown
# Team Board — Master Archive Index

Master registry for the archived team board. The Engineering Director queries **this file first** to
locate past work — never by scanning shards. Lower agents don't read it.

**How to use (retrieval funnel):**
1. **Recall (deterministic):** `grep` this file by keyword, or filter by `Category`/`Tags`. One row per slug, so grep is line-oriented.
2. **Precision (semantic):** read only the `Resolution summary` of the candidate rows and pick by *meaning* — this resolves keyword collisions (same word, different context) without opening any shard.
3. **Extract:** from the chosen row's `Shard`, run `sed -n '/<!-- <slug>:START -->/,/<!-- <slug>:END -->/p' <shard-file>` to read just that section.
4. **Phrasing-drift fallback:** if keywords miss because old wording differs, filter by `Category` and read every row in that bucket — the category survives vocabulary drift.

Each entry is registered once, at archive time, by the Engineering Director. Slugs are permanent and never
reused. `Shard` is the archive file holding the full history; the section there is bracketed by
`<!-- <slug>:START -->` / `<!-- <slug>:END -->` markers.

| Slug | Category | Shard | Heading | Resolution summary | Tags |
|---|---|---|---|---|---|
``````

**`TEAM-BOARD-ARCHIVE-<NNN>.md` — create with this preamble (substitute the real zero-padded shard number for `<NNN>`), then append wrapped sections beneath it:**

``````markdown
# Team Board Archive — Shard <NNN>

Cold-storage log of fully-shipped batches pruned from the live `TEAM-BOARD.md`. Nothing here is deleted — see the `team-communication` skill's "Board maintenance" section for the protocol.

Archive layout:
- **Live board** — `TEAM-BOARD.md`: active work only.
- **Master index** — `TEAM-BOARD-INDEX.md`: the registry the Engineering Director queries FIRST (slug → shard, category, one-sentence resolution summary, tags). Find things through the index; never scan shards to locate them.
- **Shards** — `TEAM-BOARD-ARCHIVE-NNN.md`: cold storage. This is shard <NNN>, capped at 10,000 lines; when a write would exceed the cap, a new shard is opened.

Each section is wrapped in explicit boundary markers so it can be extracted deterministically, without reading the shard in full (use the real slug in place of `NNNN`):

```
sed -n '/<!-- ARCH-NNNN:START -->/,/<!-- ARCH-NNNN:END -->/p' TEAM-BOARD-ARCHIVE-<NNN>.md
```

Slugs `[ARCH-NNNN]` are permanent — unique, never reused or renumbered.

---
``````

**Archiving workflow:**
1. Confirm the finished batch is actually done, and well-formed. Every entry tied to it must (a) use the mandatory entry format (`### [ROLE-timestamp]` + all five fields) and (b) be `**Status:** RESOLVED`, with no agent still holding open work. If a freeform note slipped onto the board, its author reformats it (or you normalize it) **before** archiving — the archive should only ever accrue well-formed entries going forward. Don't archive a batch that's still in flight.
2. **Evaluate for a knowledge-base lesson (do this while the context is fresh, before archiving buries it).** Ask whether resolving this issue taught something *generalizable* — a lesson that would transfer to a different project (per the `knowledge-base` skill's four-part inclusion test: transferable, non-obvious, actionable, durable). Most issues won't qualify; that's fine. If one does, **propose** it in your final report as a KB candidate (a one-line `Principle` + `Trigger` + why it generalizes) — you must not write to the KB yourself (policy: the top-level session is its single curator, which avoids index races and keeps the inclusion bar consistent; see the `knowledge-base` skill's "Who curates"), so the top-level session records it via that skill's RECORD protocol. This is only a forcing function to catch per-issue lessons while they're fresh; it is **not** a prerequisite for archiving, and the KB can be added to anytime afterward (the most general lessons are cross-issue and only surface later, during consolidation). Don't block the archive on it.
3. **Capacity check + shard rotation.** Find the highest-numbered shard and its line count (`wc -l`). If appending this batch would push it past **10,000 lines**, close it and open the next shard (`TEAM-BOARD-ARCHIVE-<NNN+1>.md`) before writing any content, using the canonical shard preamble from "Bootstrapping the tiers" above (substitute the new shard number). Otherwise use the current highest shard. **No shard yet (first archive in this project) → create `TEAM-BOARD-ARCHIVE-001.md` from that same canonical preamble** — don't improvise one, and don't try to "copy from an existing shard" when none exists.
4. **Assign the slug.** Next number = max existing `[ARCH-NNNN]` across *all* shards + 1 (`grep -hoE '\[ARCH-[0-9]+\]' TEAM-BOARD-ARCHIVE-*.md`). **Base case: if that grep returns nothing (first archive in this project), start at `ARCH-0001`.** Always 4-digit zero-padded. Slugs are permanent, globally unique, **never reused or renumbered** — old sections and in-body cross-references (`see [ARCH-0013]`) must keep resolving. One slug per issue (or, for a bulk legacy bundle, per batch).
5. **Wrap and append the section.** Append the full history to the chosen shard at EOF, bracketed in explicit boundary markers so it extracts deterministically regardless of line shifts:
   ```
   <!-- ARCH-NNNN:START -->
   # [ARCH-NNNN] <keyword-rich heading: issue, roles, key filenames>
   …full section text…
   <!-- ARCH-NNNN:END -->
   ```
   Verify the pair is well-formed before moving on (`grep -c` the START and END for that slug → 1 each). Do **not** store line numbers anywhere; the markers are the boundary.
6. **Register one index row** in `TEAM-BOARD-INDEX.md`, appended to the table. **If the index doesn't exist yet (first archive in this project), create it from the canonical template in "Bootstrapping the tiers" above first** — header, funnel instructions, and table header — then append your row. Never improvise the index's structure; the retrieval protocol depends on those exact columns.
   `| ARCH-NNNN | <category> | <NNN> | <heading> | <one-sentence: what failed + how fixed> | <tags> |`
   - **Shard** is the zero-padded shard **number only** (e.g. `001`) — *not* a filename. Retrieval derives the file as `TEAM-BOARD-ARCHIVE-<Shard>.md`.
   - **Category** is a broad functional bucket (e.g. `export`, `auth`, `ui-layout`, `deployment`) that groups related work for conceptual search — reuse an existing category name when one fits. (In a fresh index there are none to reuse, so coin one; that's expected.)
   - **Resolution summary** must *disambiguate*, not just describe: include the distinguishing detail (`all-time export dropping month-separator rows`), not the shared keyword alone (`export bug`). This one sentence is what lets a future lookup resolve keyword collisions without opening the shard.
   - **Tags**: condensed technical keywords/components.
7. **Verify before you wipe the source — this gates the destructive reset.** Cross-check that the index's slug set now exactly equals the `:START`-marker set across all shards (`diff` the two slug lists). They must match — a mismatch means a dropped index row or an unwrapped/duplicated section. **Only proceed to the reset if they match**; otherwise fix the archive first. This is the safety gate: resetting the board before the archive write is confirmed intact would lose the source with no clean copy. (It's a milder, detectable failure than the old line-number drift — but only if you actually check *here*, before the reset in step 8.)
8. Reset `TEAM-BOARD.md` back to the empty starting template (from step 4 of the path-resolution list above).
9. If any entries on the board belong to a different batch that's still open, leave those in the live board — only archive the resolved batch, don't wipe active work.
10. If the director's first read of the board in a session turns up an older, fully-resolved batch nobody archived (bloat carried over from a prior session), archive it before dispatching anyone rather than deferring cleanup.

No other role truncates, resets, removes, or archives entries — confirming nothing is still open, and keeping the index in sync, requires the director's cross-role view.

## Consulting the archive (engineering-director only)

The archive (index + shards) is a write-mostly historical store, not part of routine reading — don't fold it into the "read the board before starting work" step above, and never `Read` a shard in full. It exists precisely so agents *don't* load thousands of lines of old batches into context on every dispatch. **All retrieval goes through `TEAM-BOARD-INDEX.md` first** — never scan shards to find something.

**When to consult it** — only on a specific trigger, not proactively:
- A new request appears to relate to a feature/area whose board trail was already archived (e.g. the user references past work by name, or a bug looks like a regression in something previously shipped).
- A deployed agent's finding references a decision, contract, or constraint that isn't in the live board and might be sitting in an old batch (e.g. an architecture contract like a prior auth/schema decision).
- You (the director) need to confirm whether something was already tried, decided, or ruled out before routing a new request the same way again.

**How to consult it — a two-stage funnel: deterministic recall, then semantic precision.** Do not compute similarity scores, TF-IDF, or fuzzy string distance — you are a semantic reasoner; the index is built so that plain grep + your own judgment beats any lexical scoring, with far less machinery.

1. **Recall (deterministic, cheap):** `grep` `TEAM-BOARD-INDEX.md` for the keyword/role/filename, and/or filter by `Category`. One row per section, so grep is line-oriented and token-light. This yields a *candidate set*, not an answer.
2. **Precision (semantic — this resolves keyword collisions):** read only the **`Resolution summary`** cells of the candidate rows and pick by *meaning*. The same word can appear in unrelated sections (three "export" tickets, two "date" fixes); the one-sentence summary tells you which one shares the *current* problem's context. Bypass rows whose summary describes a different situation, even if they matched the keyword. **Never extract a full section straight off a keyword hit — gate every extraction through the summary.**
3. **Extract (targeted, deterministic):** from the chosen row read the `Slug` and `Shard`, then pull exactly that section — boundary-matched, so line shifts never matter:
   ```
   sed -n '/<!-- <slug>:START -->/,/<!-- <slug>:END -->/p' TEAM-BOARD-ARCHIVE-<NNN>.md
   ```
   Read only that block into context. Nothing else from the shard.
4. **If two candidates remain genuinely plausible after their summaries** — don't guess. Read just the first few lines of the single most-likely section to check its symptom against the current one, or surface the ambiguity to whoever asked (`two archived export issues — [ARCH-0003] download-bug vs [ARCH-0001] export-feature; which matches?`). This is "escalate, don't guess" applied to retrieval.
5. **After extraction, confidence-check the fit** (per the `confidence-check` skill): confirm the section actually addresses the current question before feeding it downstream. If it's the wrong context, discard and re-triage rather than force-fitting it.

**Phrasing-drift fallback (conceptual search).** When keyword recall misses because the old issue used different wording for a similar problem: filter the index by `Category` (broad functional area) and read every row in that bucket. The category survives vocabulary drift, and reading a module's summaries in sequence lets you trace how that feature evolved across sections without opening a single shard.

**Scale trigger — when to add embeddings (not before).** While a category's rows fit comfortably in one read, the director reading the summaries directly *is* the best semantic retrieval available — an LLM understands context and nuance that any similarity score flattens, so embeddings would be strictly worse *and* add machinery (a model runtime, a vector store, a re-embed step on every archive, possible data egress). Only when a single `Category` grows past what's practical to read in one pass (order of many hundreds to thousands of rows) does pre-ranking start saving more than it costs. At that point — and only then — the principled add-on is **embeddings/vector similarity over the `Resolution summary` column**: embed each summary once (re-embed on archive), and at query time embed the request and cosine-rank to shortlist candidates, then continue the existing funnel unchanged (read the shortlisted summaries → gate → sed-extract). No restructure is needed — the summaries are already the right text to embed, so this bolts onto the *front* of the recall stage. Do **not** reach for TF-IDF or fuzzy string distance instead: TF-IDF is statistically meaningless on a small corpus and blind to meaning on any, and fuzzy matching is edit-distance, not semantics.

**Sanity check (loud, not silent):** the index's slug set must equal the shards' `:START`-marker set. If a slug is in one but not the other, the archive is malformed (dropped index row or unwrapped section) — fix it rather than trusting the read. There is no line-number integrity check because no line numbers are stored anywhere; boundaries come from markers every time.

No other role consults the index or the shards — it's not part of their mesh-visibility responsibility, and giving every dispatched agent a reason to read the archive would reintroduce the exact context bloat archiving was meant to eliminate.

## Respecting the hierarchy

Mesh visibility is not decision authority. Seeing another role's entry doesn't mean you act on it yourself if it's outside your remit — route it per `team-orchestration`'s escalation rules:
- A junior dev seeing a senior dev's entry follows it; they don't override it.
- A concern tagged `For: tech-lead` waits for tech-lead to resolve it, even if you can see it on the board — don't unilaterally decide a cross-cutting question because you spotted the entry first.
- If two entries on the board conflict, that's a signal for escalation (to `tech-lead` for technical conflicts, `project-manager` for scope/priority, `engineering-director` for a final call) — not something to resolve by whichever agent gets there first.

## Anti-patterns
- **Race conditions are real and unhandled.** There's no file locking — if two agents read-then-write at nearly the same moment, one's append can be lost. Minimize the window (read right before you write, don't hold the read open while doing other work), but don't treat this as airtight. If you suspect you lost an entry (the board looks like it's missing something you expected), say so rather than assuming it's fine.
- Don't rewrite or delete another agent's entry text — only your own status line via a scoped `Edit`.
- Don't use the board as a substitute for actually doing your own job — it's for things outside your scope or useful to a related role, not a dumping ground to avoid making a decision you're equipped to make.
- Don't let mesh entries trigger unbounded back-and-forth between roles — log it once, clearly, and let the correct owner (per the hierarchy) act on it.
