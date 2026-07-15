---
name: project-management
description: Use when breaking a feature/request into tasks, planning a sprint, sequencing work across frontend/backend/QA, or resolving cross-team blockers. Primary skill for the project-manager subagent.
---

# Project Management

## Workflow
1. **Clarify scope** — restate the request in one sentence; if it's ambiguous on what "done" means, flag it before planning.
2. **Decompose** — break into the smallest set of independently completable tasks. Each task should map to one role (frontend, backend, QA, DevOps, etc.).
3. **Sequence** — identify dependencies (e.g., backend API must exist before frontend integration). Order tasks accordingly; mark which can run in parallel.
4. **Assign** — name which subagent/role owns each task.
5. **Track** — use TaskCreate/TaskUpdate to record tasks and statuses; update status the moment work starts or finishes, don't batch.
6. **Risk check** — call out anything that could slip (unclear requirements, external dependency, missing test coverage) before work starts, not after.

## Output format
Produce a short punch list:
- Task — Owner role — Depends on — Status

## Anti-patterns to avoid
- Don't create process for its own sake (no status-update rituals, no meeting-shaped output).
- Don't let scope grow silently — if a request implies more than originally stated, surface it explicitly rather than quietly expanding the plan.
- Don't assign senior-level architecture decisions to junior roles.
