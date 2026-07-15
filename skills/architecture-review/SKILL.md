---
name: architecture-review
description: Use when deciding system architecture, evaluating tradeoffs between competing technical approaches, or setting coding standards before implementation starts. Primary skill for the tech-lead subagent.
---

# Architecture Review

## Workflow
1. **State the requirement** in concrete terms — throughput, consistency needs, team size, time horizon. Don't design for hypothetical scale.
2. **List viable approaches** (2-3 max) with their real tradeoffs: complexity, cost, maintainability, time-to-ship.
3. **Pick the simplest approach that satisfies the actual requirement.** Justify why more complex alternatives are premature.
4. **Define boundaries** — what each component owns, how data flows between frontend/backend/DB, what contracts (API shapes) are stable.
5. **Set the standard once** — coding conventions, error handling pattern, naming — and write it down so junior/senior devs aren't reinventing it per-feature.

## Red flags to call out
- Speculative abstraction for "future flexibility" with no concrete near-term need
- New dependency/framework introduced for a problem the existing stack already solves
- Inconsistent patterns across frontend/backend for the same kind of problem (e.g., two different error-handling conventions)

## Output format
Decision, 1-2 sentence rationale, and the concrete boundaries/contracts that follow from it. Skip exhaustive option surveys — give the recommendation.
