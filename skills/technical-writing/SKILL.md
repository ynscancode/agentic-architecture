---
name: technical-writing
description: Use when writing or updating documentation, API references, READMEs, changelogs, or onboarding guides. Primary skill for the technical-writer subagent.
---

# Technical Writing

## Workflow
1. **Verify against code, not memory** — before documenting behavior (an API's params, a config option's default), check the actual current source rather than assuming it matches prior docs.
2. **Write for the target reader** — end-user docs explain usage and outcomes; contributor docs explain structure, setup, and rationale for non-obvious decisions.
3. **Be concise** — document intent and non-obvious behavior; skip what's already clear from well-named code/APIs.
4. **Keep docs in sync** — when code changes, check if existing docs now contradict it; flag or fix stale sections rather than leaving them.

## Checklist before finishing
- [ ] Every claim about behavior/parameters checked against current code
- [ ] No redundant restatement of self-evident code
- [ ] Audience-appropriate depth (user-facing vs. contributor-facing)
- [ ] Only created new files if explicitly requested; otherwise updated existing docs
