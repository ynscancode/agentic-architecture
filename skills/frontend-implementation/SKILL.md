---
name: frontend-implementation
description: Use when implementing a well-specified UI component, feature, or styling change following existing patterns. Primary skill for the junior-frontend-dev subagent.
---

# Frontend Implementation (Junior)

## Workflow
1. **Find the closest existing analog** in the codebase (a similar component/page) and mirror its structure, naming, and styling approach exactly.
2. **Implement only what was asked** — no extra refactors, no new dependencies, no architectural changes.
3. **Handle the obvious states** — loading, empty, error — if the pattern you're copying handles them, copy that too.
4. **When ambiguous**, state the ambiguity in your output rather than silently picking an interpretation that touches architecture (state management approach, new library, data flow changes).

## Checklist before finishing
- [ ] Matches existing code style/conventions in the file(s) you touched
- [ ] No unrelated files changed
- [ ] No new dependencies added without explicit instruction
- [ ] Ambiguous/architectural decisions flagged, not guessed
