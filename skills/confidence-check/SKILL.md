---
name: confidence-check
description: Use after completing any task or subtask, before reporting it done or moving to the next step. Mandatory self-verification gate for all dev-team agents — confidence must reach 100% before proceeding.
---

# Confidence Level Check

A mandatory gate run after finishing any task or subtask, before declaring it done or handing off to the next step/agent.

## Procedure

1. **State what was supposed to happen.** Restate the task/spec/acceptance criteria in one line.
2. **Verify, don't assume.** Check the actual result against that line:
   - Code: run it, run existing tests, re-read the diff against the requirement.
   - Data/schema: check actual state, not intended state.
   - Docs/specs: re-read against the source of truth (code, requirements) they describe.
   - Design/handoff: check it's consistent with existing patterns and covers the states it claims to cover (error/empty/edge cases).
3. **Assign a confidence level (0-100%)** based on actual verification performed, not gut feel:
   - 100% — verified directly (ran it, tested it, read the exact lines that prove it), no untested assumptions, no skipped edge cases relevant to the task.
   - <100% — anything unverified, assumed, partially tested, or with a known gap.
4. **If confidence < 100%:** identify exactly what's unverified or wrong, fix or re-verify it, and repeat the check. Do not proceed or report completion at less than 100%.
5. **If 100% is genuinely unreachable** (e.g., no way to run the code in this environment, external dependency unavailable), say so explicitly instead of inflating the number — state the real confidence level and exactly what's untested, so the human or next agent knows the gap.

## What "100%" requires concretely
- The specific claim being made was actually checked, not inferred from similar past behavior.
- All states/edge cases in scope for the task were addressed, not just the golden path.
- No "should work" / "this likely fixes it" language in the final report — only "verified: <how>".

## Anti-patterns
- Declaring confidence based on code looking correct without executing it when execution is possible.
- Rounding 80-95% up to 100% to avoid another refactor pass.
- Skipping the check on "small" subtasks — small tasks still get the gate, just a faster pass through it.
