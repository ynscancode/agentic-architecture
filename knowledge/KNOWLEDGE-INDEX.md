# Universal Knowledge Base — Master Index

Cross-project cognitive library of **generalizable** lessons. Consult this first (never scan shards).
Governed by the `knowledge-base` skill — see it for inclusion criteria, the write/consult/consolidation
protocol, and the boundary with per-project memory.

**Retrieval funnel (recall → precision):**
1. **Recall:** `grep` this file by the current problem's keywords, or filter by `Category`. One row per lesson.
2. **Precision:** read the `Trigger` and `Principle` of the candidates — match the *current situation* against `Trigger`, not just shared words. Pick by meaning.
3. **Extract (only if you need the full write-up):** `sed -n '/<!-- <slug>:START -->/,/<!-- <slug>:END -->/p' KNOWLEDGE-<NNN>.md`.
4. Check `Status` before trusting a row: skip `superseded-by-*` (follow the pointer) and `deprecated` (a past application proved it wrong); for `active ⚠N`, extract the section and read its **Misfire receipts** first — the lesson misfired before, and the receipts say the context(s) where it does NOT apply.

**Do not** compute TF-IDF/fuzzy/similarity scores. Grep for recall + your own judgment for precision.

`Status` values: `active` (clean) · `active ⚠N` (has N **misfire receipts** — read them in the shard before applying) · `deprecated` (a past application proved it wrong — skip, no successor) · `superseded-by-KB-XXXX` (replaced by a more general lesson after consolidation; kept for provenance).
`Principle` is the compressed, transferable rule. `Trigger` is the situation that should make you recall it.

> **This index ships empty by design.** The knowledge base is meant to be *earned* — each row is a lesson
> your own sessions learned the hard way, not a preloaded list of best practices. The first `RECORD` pass
> creates `KNOWLEDGE-001.md` and appends the first row below. See the `knowledge-base` skill's RECORD
> protocol; the base case (`grep` returns nothing) starts at `KB-0001`.

| Slug | Category | Shard | Status | Principle (compressed) | Trigger (when to recall) | Tags |
|---|---|---|---|---|---|---|

---

## Consolidation watermarks

Bookkeeping for the CONSOLIDATION trigger — **not** part of retrieval. Ignore this table when consulting;
it holds no lessons.

One row per category that has been consolidated at least once. `Watermark` is the highest `KB-NNNN` in
existence when that category's last pass ran, so "added since the last pass" = that category's
`Status: active` rows with a **higher** slug. A category with no row here has never been consolidated —
treat its watermark as `KB-0000` and count all of its active lessons.

The trigger deliberately measures **new material, not standing inventory**: a pass over genuinely
distinct lessons merges nothing, so a total-active count would stay armed and re-fire a fruitless pass
on every subsequent write to that category, forever. **A pass that finds nothing to merge still updates
its watermark** — "these are distinct" is a result, not a skipped pass.

| Category | Last pass | Watermark |
|---|---|---|
