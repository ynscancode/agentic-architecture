---
name: qa-testing
description: Use when testing a feature, verifying a bug fix, writing test cases, running regression checks, or auditing an implementation against its spec. Primary skill for the qa-engineer subagent.
---

# QA / Testing

## Workflow
1. **Restate the spec/expected behavior** before testing — confirms you're testing the right thing.
2. **Test the golden path first**, then deliberately probe edge cases: empty input, max/min boundaries, invalid input, concurrent access, permission boundaries.
3. **For bug fixes**: reproduce the original bug first (confirm it existed), then confirm the fix resolves it, then check for regressions in adjacent functionality.
4. **Run, don't assume** — actually execute tests/commands and report real pass/fail output. Never report "should work" as a result.
5. **Coverage audit** — explicitly call out what's untested if a full test pass isn't feasible (e.g., no UI testing capability, no access to a staging env).

## Output format
- What was tested, how (command/method), and the actual result (pass/fail with evidence).
- Discrepancies vs. spec, listed concretely with reproduction steps.
- Gaps in coverage, stated explicitly rather than implied.

## Anti-patterns
- Don't mark something verified without running it.
- Don't treat "no errors thrown" as equivalent to "behaves correctly" — check actual output/state.
