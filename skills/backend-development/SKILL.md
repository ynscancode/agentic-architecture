---
name: backend-development
description: Use when designing APIs, modeling data, handling scalability/concurrency concerns, or reviewing junior backend work. Primary skill for the senior-backend-dev subagent.
---

# Backend Development (Senior)

## Workflow
1. **Design the contract first** — request/response shape, status codes, error format — before implementation. Keep it consistent with existing endpoints.
2. **Data modeling** — normalize by default; denormalize only with a measured performance reason. Define constraints (uniqueness, foreign keys, required fields) at the data layer, not just app logic.
3. **Validate at boundaries only** — user input and external API responses. Trust internal function contracts and framework guarantees; don't re-validate data that's already been validated upstream.
4. **Concurrency/scale** — check for race conditions on shared state, N+1 queries, and missing indexes on new query patterns before merging.
5. **Reviewing juniors** — check for: missing edge-case handling, inconsistent error responses, unscoped changes, and validation logic duplicated instead of reused.

## Anti-patterns
- Don't add defensive error handling for conditions that can't occur given the call site.
- Don't introduce a new pattern (e.g., different error envelope) inconsistent with existing endpoints.
- Run the test suite after changes when one exists — don't assume correctness.
