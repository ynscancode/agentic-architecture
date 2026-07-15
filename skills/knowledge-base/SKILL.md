---
name: knowledge-base
description: Universal, cross-project cognitive library of generalizable lessons learned from resolved issues. Use in THREE situations. (1) RECORD — after resolving a problem whose lesson would transfer to a *different* project (a non-obvious gotcha, a design principle, a debugging insight, a corrected mistake), capture it here. (2) CONSULT — before non-trivial technical work of ANY kind, not just design decisions: whenever you touch an area the KB has lessons about (e.g. dates/timezones, auth, migrations/schema, CSS layout, deployment, retrieval), debug something non-obvious, pick between approaches, or make a judgment call — check whether a past lesson applies so you don't repeat a mistake already learned. Bias toward looking; a grep is nearly free and an empty result is normal. (3) MISFIRE — after applying a lesson pulled from the KB that turned out wrong or inapplicable in this context, file an error receipt so the next retrieval carries the warning. Not for project-specific facts (those go in per-project memory).
---

# Universal Knowledge Base

A compounding, self-improving library of **generalizable** lessons that persists across every project and
session. It lives in `~/.claude/knowledge/` (alongside `agents/` and `skills/`), so it applies to Claude
universally — not scoped to any one repo. The goal is continuous improvement: capture what was learned the
hard way once, retrieve it before repeating the mistake, and periodically compress many specific lessons
into fewer, sharper principles.

## What belongs here — the inclusion test (be strict; precision over volume)

A lesson qualifies only if it is **all four**:
1. **Transferable** — it would change how you approach a *different* task in a *different* project, not just this one.
2. **Non-obvious** — it isn't already-default best practice; it's something worth having learned (often from a mistake or a rejected approach).
3. **Actionable** — it can be phrased as guidance that changes future behavior, not a mere observation.
4. **Durable** — it isn't tied to a version/API that will change next week (or if partly time-bound, say so in the entry).

**Negative test — does NOT belong here** (goes to per-project memory instead): anything specific to one project — its file paths, schema, config, conventions, this user's preferences, or a fix that only makes sense inside that codebase. Litmus: *"Would this help on an unrelated project six months from now?"* If no, it's memory, not knowledge.

**Boundary with the memory system:** per-project memory (`~/.claude/projects/<proj>/memory/`) holds *facts about a specific project/user*. This knowledge base holds *portable principles*. When in doubt, a lesson that names a specific file/repo is memory; a lesson that states a general rule is knowledge. Don't duplicate across both.

## Structure (same infrastructure as the team-board archive)

- **Master index** — `~/.claude/knowledge/KNOWLEDGE-INDEX.md`: one row per lesson (`Slug | Category | Shard | Status | Principle | Trigger | Tags`). Query this first. It also carries a small **Consolidation watermarks** table (one row per category that has been consolidated) — bookkeeping for the CONSOLIDATION trigger, not part of retrieval; ignore it when consulting.
- **Shards** — `~/.claude/knowledge/KNOWLEDGE-NNN.md`: full lesson text, each wrapped in `<!-- KB-NNNN:START -->` / `<!-- KB-NNNN:END -->` markers. **10,000-line cap per shard.**
- Slugs `[KB-NNNN]` are permanent and never reused. No line numbers are stored — boundaries come from markers.

### Bootstrapping a shard

The index ships (or is created) empty; **shards are created lazily, at the first RECORD.** A fresh install therefore has *zero* shards, and the first lesson recorded on it must create `KNOWLEDGE-001.md`. Shard rotation later (`-002`, `-003`, …) uses this same template.

**Use this preamble verbatim — do not improvise one, and don't try to "copy an existing shard" when none exists.** Every install's shards must be identical in structure, or the retrieval protocol (which assumes these exact marker formats) breaks. Substitute the real zero-padded shard number for `<NNN>`, then append wrapped lessons beneath it:

``````markdown
# Universal Knowledge Base — Shard <NNN>

Cross-project cognitive library: generalizable, transferable lessons distilled from resolved issues.
**Universal**, not project-specific — applies to Claude's work everywhere. Governed by the
`knowledge-base` skill (inclusion criteria, write/consult/consolidation protocol).

Two-tier store, same infrastructure as the team-board archive:
- **Master index** — `KNOWLEDGE-INDEX.md`: one row per lesson (slug, category, shard, status, principle, trigger, tags). Queried first; holds the compressed principle, not the full write-up.
- **Shards** — `KNOWLEDGE-NNN.md`: full lesson text. This is shard <NNN>, capped at 10,000 lines.

Each lesson is wrapped in explicit boundary markers for deterministic extraction (use the real slug for `NNNN`):

```
sed -n '/<!-- KB-NNNN:START -->/,/<!-- KB-NNNN:END -->/p' KNOWLEDGE-<NNN>.md
```

Slugs `[KB-NNNN]` are permanent — never reused. A lesson may be **superseded** by a more general one
(its `Status` points at the successor) but is never deleted, so provenance survives compression.

---
``````

## Who curates

The **top-level session** owns writes and consolidation. Subagents (e.g. `engineering-director`) **must not write here** — a subagent **proposes** a candidate lesson in its final report, and the top-level session decides whether it clears the inclusion test and records it. Consulting (reading) is open to whoever needs it.

**This is a policy, not a sandbox barrier.** Verified by probe (2026-07-15): a subagent can read *and* **write** under `~/.claude/` — the write was not denied, no prompt. So this separation holds only if followed deliberately. Two reasons it's worth following:
1. **Single-writer avoids races.** There's no file locking; concurrent subagent writes to `KNOWLEDGE-INDEX.md` would silently lose entries (the same unhandled race the team board has).
2. **Curation quality.** The inclusion test needs the whole-session, cross-project view. A subagent sees one batch and will over-record — exactly the noise inflation this KB is designed to prevent. One curator keeps the bar consistent.

If you want a hard barrier rather than discipline, add a permission deny-rule for `~/.claude/knowledge/**` — nothing in the runtime enforces it today.

## CONSULT protocol (retrieval funnel — recall, then precision)

**Trigger — bias toward consulting; under-use is the real failure mode.** Most lessons here are *domain gotchas* that fire on the **kind of code you're touching**, not on a conscious "I am now making a design decision" moment — a decision-shaped trigger under-fires and the library goes unread. (Check the lessons' own `Trigger` fields: several fire on *touching date code*, *writing a migration*, *touching auth*, or *debugging a layout symptom* — none of which feel like decisions.) Consult when you're about to:
- do non-trivial work in an area the KB covers — **skim the `Category` column; it is the map of what's known.** (Deliberately not duplicated as a hardcoded list here: it would drift as categories are added — see KB-0008.)
- debug something non-obvious, or that feels familiar / like a shape you've hit before;
- pick between approaches, or make a design/architecture call;
- make a judgment call you can't fully justify from the code in front of you.

**The cost asymmetry is the whole argument:** the index is one line per lesson, a grep is nearly free, and an empty result is the *normal, expected* outcome — while skipping the check risks repeating a mistake that is already written down. **Skip only genuinely trivial mechanical work** (a rename, a typo, running a test). If in doubt, look.

1. **Recall (deterministic):** `grep` `KNOWLEDGE-INDEX.md` for the current problem's keywords, or filter by `Category`. **Run it as a Bash command ending in `# CONSULT`** — that marker is the only thing that distinguishes a lookup from the KB's own bookkeeping, and the health check (RECORD step 7) counts nothing else:
   ```bash
   grep -i "<keyword-or-category>" ~/.claude/knowledge/KNOWLEDGE-INDEX.md   # CONSULT
   ```
   Use Bash here rather than the `Grep`/`Read` tools — they have nowhere to carry the marker, so a consult made through them is invisible and counts as zero. If you forget the marker the log undercounts, which is the safe direction (a low count sends someone to look); inferring intent from the command's shape would fail the other way.
2. **Precision (semantic):** read the `Trigger` and `Principle` of the candidates — match the *current situation* against `Trigger`, not just shared words. This is how you avoid false-positive keyword matches (see KB-0002; do **not** compute TF-IDF/fuzzy scores).
3. **Check the candidate's `Status` before trusting it** (the receipt system's read side):
   - `superseded-by-KB-XXXX` → follow the pointer to the successor. `deprecated` → **skip it**; a past application proved it wrong, with no replacement.
   - `active ⚠N` (N ≥ 1) → the lesson has **misfire receipts**: it was applied before and turned out wrong/inapplicable. **Extract the section and read its `Misfire receipts` block before applying** — each receipt names a context where the lesson does NOT hold and what to do instead. Apply only if your situation is clearly outside those.
   - plain `active` → no recorded misfires; proceed.
4. **Extract the full write-up** if you need the detail (mandatory when `Status` carries `⚠`): `sed -n '/<!-- <slug>:START -->/,/<!-- <slug>:END -->/p' KNOWLEDGE-<NNN>.md`.
5. **Apply the principle**, and say you're doing so if it materially changes your approach. **If it later turns out wrong or inapplicable here, file a receipt** (see the MISFIRE / RECEIPT protocol) — that's how the next retrieval avoids the same mistake.
6. If nothing matches, proceed — an empty result is normal, not a failure.

## RECORD protocol

**Two entry points, both valid** — the KB is independent of any project's archive (separate IDs, no shared reads), so there is **no ordering dependency**: a lesson can be recorded before, during, or long after the originating issue is archived.
- **At resolution / archival time (forcing function):** the natural moment to catch a per-issue lesson, while context is fresh. In the team-dev setup, the `engineering-director` evaluates and *proposes* a candidate in its report (by policy — see "Who curates"; it is technically *able* to write, but must not); the top-level session records it.
- **Retrospectively (anytime):** the most *general* lessons are cross-issue — they only become visible after several issues, often during a Consolidation pass. Recording after archiving is expected and encouraged, not a fallback.

Trigger: right after resolving something whose lesson passes the four-part inclusion test. (Cross-issue patterns don't need their own separate trigger to watch for — they surface mechanically during a CONSOLIDATION pass, see its explicit trigger below, which is itself checked automatically at RECORD step 6.)

1. **Dedupe first.** Grep the index for the topic. If a near-identical lesson exists, don't add a duplicate — either it already covers this (do nothing) or this is a sharper/more general version (go to Consolidation).
2. **Pick the shard.** `ls KNOWLEDGE-[0-9]*.md` for the highest-numbered shard, then `wc -l` it: if this entry would push it past 10,000 lines, open `KNOWLEDGE-<NNN+1>.md` instead. **Base case: no shard at all (a fresh install — the index ships empty) → create `KNOWLEDGE-001.md` now.** Either way the new file starts from the canonical preamble in "Bootstrapping a shard" above — never an improvised header.
3. **Assign a slug.** `max existing KB-NNNN across all shards + 1` (`grep -hoE '\[KB-[0-9]+\]' KNOWLEDGE-*.md`). **Base case: if that grep returns nothing (empty KB), start at `KB-0001`.** Always 4-digit zero-padded. Permanent, never reused.
4. **Write the shard section**, wrapped in `<!-- KB-NNNN:START/END -->`, with: `Category`, `Status: active`, `Principle`, `Trigger`, `Context (generalized)`, `Why it generalizes`, `How to apply`, `Provenance` (date + a *generalized* description of where it arose — no project secrets). Verify the marker pair is well-formed.
5. **Register one index row** (`Slug | Category | Shard | Status | Principle | Trigger | Tags`). Keep `Principle`/`Trigger` tight and disambiguating — they carry retrieval. `Shard` is the zero-padded shard **number only** (e.g. `001`), not a filename — retrieval derives the file as `KNOWLEDGE-<Shard>.md`.
6. **Check the consolidation trigger — do this every time, not just "periodically."** The trigger fires on **new material, not standing inventory**: count this `Category`'s `Status: active` rows in `KNOWLEDGE-INDEX.md` whose slug is **higher than that category's watermark** in the index's "Consolidation watermarks" table. No row there means the category has never been consolidated — treat its watermark as `KB-0000` and count all of them. **If that count is ≥ 5**, run the CONSOLIDATION protocol on that category now, before finishing — don't defer it, since nothing else will independently notice this later. This is the mechanism that actually fires the trigger described below; without this step the consolidation rule is unenforced.
   - **Why "since the last pass" rather than "total active":** the trigger counts a category *label* — it cannot see whether the content actually overlaps, and is only a cheap proxy for "there might be redundancy here." When a category's lessons are genuinely distinct, a pass merges nothing and supersedes nothing, so a total-active count stays ≥ 5 and re-fires a **fruitless pass on every subsequent write to that category, forever**. Watermarking makes each batch of new material get evaluated exactly once.
   - Filter on `Status: active` when counting. That's also what keeps the watermark table's own rows out of the count — they carry no status.
7. **Health check — is this a graveyard? (cheap; do it here, never on a calendar.)** In `~/.claude/knowledge/CONSULT-LOG.tsv`, count the rows whose kind is **`consult`**, and note the date of the most recent one. Those are lookups that declared themselves (step 1 of CONSULT). Rows marked `other` are the KB's own bookkeeping — **never count them**; they're kept only to eyeball.
   - **This is a smoke detector, not a dashboard.** The one actionable signal is **≈0 `consult` rows over a stretch where real work happened** — meaning the CONSULT triggers aren't firing, the categories don't match the work being done, the marker isn't being used, or the `CLAUDE.md` wiring is broken. All are diagnosable; say so rather than silently continuing. **Do not build analytics on this** (KB-0002's mistake in a new costume: machinery where reading it yourself is better — at this size, `cat` the file).
   - **A pile of `other` rows next to zero `consult` rows is not health — it is the diagnosis.** It means the KB is being *maintained* but never *used*.
   - **The harness writes this log, not you** — a log you maintained would share the exact failure it measures. Never hand-write rows; if it looks wrong, fix the hook.
   - An empty log is only meaningful *after* real work has happened with the hook installed. On the first record after install there's nothing to compare against — note that and move on. Likewise, a session spent working *on* the KB produces `other` rows only; that's correct, not a fault.
8. **Consistency invariant:** the index's slug set must equal the shards' `:START`-marker set. Cross-check after writing.

## CONSOLIDATION protocol (continuous semantic compression — what makes it *compound*)

A growing pile of narrow lessons is a liability; the library must get **denser and sharper**, not just bigger.

**Trigger (explicit, checkable):** **5 or more `active` lessons have been added to a `Category` since that category's last consolidation pass** — for a category that has never been consolidated, that is simply 5 or more `active` entries. Checked automatically at RECORD step 6 above, every time a row is registered. Also run on demand if the user asks, or if you notice redundancy while consulting the KB for an unrelated task (opportunistic — not required, but don't ignore it if you spot it). Do not wait for a separate "periodic" pass; the count check at RECORD step 6 is what makes this actually happen instead of sitting as an unmonitored guideline.

The trigger measures *new material*, not standing inventory — see RECORD step 6 for why a total-active count re-fires forever on a category whose lessons turn out to be genuinely distinct. Note the pass itself still considers the **whole** category (step 1), not just the new arrivals: a new lesson often subsumes an old one, and cross-cutting patterns only surface across the full set. It's the *trigger* that's scoped to new material, not the comparison.

Compression pass, once triggered — **runs off the index, not full shard reads** (same recall-then-extract discipline as CONSULT; you do *not* read every lesson's full body):

1. **Compare from the index.** `grep` the category in `KNOWLEDGE-INDEX.md` and read only the `Principle` and `Trigger` cells of those rows — one line each, the compressed layer exists exactly so this scan is cheap. That's enough to spot which lessons express the same underlying rule. Do not extract shard bodies to *find* overlap.
2. **Extract only what you'll merge.** Once you've identified the specific 2–4 lessons that collapse into one, `sed`-extract *just those* shard entries — so you can preserve their concrete specifics and cross-reference them — then **write one higher-order principle** (new slug) that subsumes them. The other category rows you never opened stay unread.
3. Mark the subsumed entries `Status: superseded-by-KB-XXXX` (never delete — provenance and the specific cases stay reachable). Point the successor's `Context` back at them.
4. Merge near-duplicates the same way. Prune nothing outright; supersede instead.
5. **Record the watermark — do this even if you merged nothing.** In `KNOWLEDGE-INDEX.md`'s "Consolidation watermarks" table, set this category's row to today's date and the highest `KB-NNNN` now in existence (add the row if this was the category's first pass). Do this *after* writing any successor, so the successor isn't counted as new material toward the next trigger. **A pass that found nothing to merge is a completed pass, not a skipped one** — "these lessons are genuinely distinct" is a result, and recording it is exactly what stops the trigger re-firing on every subsequent write to the category. Skipping this step re-creates the bug the watermark exists to fix.
6. Retrieval skips `superseded-*` rows by default, so the active surface stays small even as history grows.

Bias every step toward **fewer, more general, more actionable** entries. A handful of sharp principles beats a hundred vague notes.

## MISFIRE / RECEIPT protocol (closing the loop on wrong retrievals)

The KB improves not only by *adding* lessons but by recording when one **misled you**, so the next retrieval carries the warning. **Asymmetric by design: file a receipt only for a FAILED application — never for a correct/applicable one** (logging successes would just be noise). A receipt lives *on the lesson* (co-located, not in a separate file) so it can't be retrieved without being seen.

**Trigger:** you retrieved a lesson via CONSULT, applied it (or were about to), and it turned out **wrong** or **inapplicable in this context**.

**File the receipt** (top-level session curates; subagents **must not** write here by policy — see "Who curates" — so they flag the misfire in their report and the top-level session records it):
1. **Append the receipt to the lesson's shard entry**, under a `- **Misfire receipts:**` bullet (create the bullet if it's the first one):
   `  - ⚠ <YYYY-MM-DD> — retrieved for <the situation>; turned out <wrong | inapplicable> because <reason>. Takeaway: <corrected scope / what to do instead>.`
2. **Raise the flag on the index row** so recall catches it: change that row's `Status` from `active` to `active ⚠N`, where `N` is the number of receipts now on the lesson. Without this flag the receipt is invisible at recall — this is the wired link that makes CONSULT step 3 fire.
3. **Remediate by failure mode:**
   - **Inapplicable** (the principle is right but got pulled for the wrong situation — the common case): sharpen the lesson's `Trigger` with an explicit **anti-trigger** ("does NOT apply when …") capturing the boundary the misfire exposed. The receipt logs the instance; the sharpened Trigger prevents the recurrence.
   - **Wrong** (the principle itself is flawed): if fixable, correct the `Principle`/`How to apply` and note the correction in the receipt. If unsound with no fix, set `Status: deprecated` (retrieval skips it, like superseded, but with no successor) and say why in the receipt.
4. **Consistency:** receipts never touch slugs or markers, so the index↔shard slug invariant is unaffected — but confirm the `⚠N` count on the index row equals the number of receipt bullets in the shard entry.

Receipts are permanent and append-only, like the lessons — provenance of what was learned the hard way, and the guardrail against learning it twice.

## Anti-patterns
- **Write-only graveyard.** The library only self-improves if it's actually *consulted*. If you never read it, it changes nothing. Consult on the triggers above, not just when convenient.
- **Noise inflation.** Recording obvious best-practices or project-specific trivia dilutes signal. When unsure, apply the four-part test honestly; most candidate "lessons" fail it.
- **Duplicate-with-memory.** Don't mirror a project fact here and in memory. Portable principle → here; project fact → memory.
- **Slug reuse / line-number references.** Slugs are permanent; boundaries are markers, never line numbers.
- **Silent misfire.** Applying a retrieved lesson that turned out wrong/inapplicable and *not* filing a receipt — so the next agent (or you) repeats the exact mistake. The receipt is cheap; the repeated mistake isn't.
