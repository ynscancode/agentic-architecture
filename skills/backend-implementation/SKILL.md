---
name: backend-implementation
description: Use when implementing a well-specified endpoint, CRUD operation, or backend bug fix following existing patterns. Primary skill for the junior-backend-dev subagent.
---

# Backend Implementation (Junior)

## Workflow
1. **Find the closest existing endpoint/module** and mirror its structure: routing, validation, error handling, response shape.
2. **Implement only what was asked** — no schema changes, no new dependencies, no architecture decisions without flagging them first.
3. **Match existing error-handling conventions exactly** (status codes, error envelope shape).
4. **When ambiguous** on data modeling or architecture, state the ambiguity in your output instead of deciding unilaterally.

## Checklist before finishing
- [ ] Matches existing routing/validation/error patterns
- [ ] No unrelated files or schema changes
- [ ] No new dependencies added without explicit instruction
- [ ] Architecture-level ambiguities flagged, not guessed
