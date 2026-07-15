---
name: database-administration
description: Use when designing schemas, writing/reviewing migrations, optimizing slow queries, or planning indexing strategy. Primary skill for the dba subagent.
---

# Database Administration

## Workflow
1. **Schema design** — normalize by default; define constraints (NOT NULL, unique, foreign keys) at the DB level so invalid states are unrepresentable, not just discouraged.
2. **Migrations** — prefer additive, backward-compatible changes (add column nullable/with default, backfill separately, then tighten constraints in a later migration). Never assume a migration is safe on a large/production table without considering locking behavior.
3. **Query optimization** — get the query plan (EXPLAIN) before guessing at an index; add indexes for actual query patterns, not speculative ones.
4. **Destructive changes** (dropping columns/tables, NOT NULL on existing data, type changes) — flag explicitly and confirm before applying, even if asked directly, since these are hard to reverse.

## Safety checklist for any migration
- [ ] Reversible, or has a clear rollback plan
- [ ] Won't lock a large table for an unacceptable duration
- [ ] Backfill (if any) is a separate step from constraint tightening
- [ ] Tested against representative data volume, not just an empty dev DB
