---
name: visual-verification
description: Use when building, reviewing, or specifying UI/UX work — verify the actual rendered app instead of judging UI correctness from code alone. Primary skill for senior-frontend-dev, junior-frontend-dev, ui-ux-designer, qa-engineer, and product-owner when reviewing UI-facing work, and for whoever holds the live browser tool connection (confirmed: the top-level interactive session, not subagents — see below).
---

# Visual Verification

Code that "looks right" can still render wrong. This skill makes checking the running app a required step, not an optional one, whenever the task touches what a user actually sees.

## Important: who can actually do this

`mcp__playwright__*` tools use a `stdio` MCP transport — a process-exclusive pipe to whichever process started the server. This was confirmed empirically: it works in the top-level interactive session, but a subagent spawned via the Agent tool runs in a separate process and does not get a connection to that same instance. **If you are a subagent (any of the 14 team roles, including when engineering-director itself is invoked as a subagent), assume you do NOT have a working Playwright connection unless you've just confirmed otherwise in this exact session.**

Do not fake a screenshot result, infer "it probably renders fine" to skip the check, or silently drop the verification step. Instead:

1. **Try calling a Playwright tool once** (e.g. `browser_navigate`) if it appears in your tool list. If it errors or the tool isn't available, stop trying — don't retry-loop.
2. **Post a visual-verification request** via `team-communication`'s team board: what to check (URL/route, component, specific state — loading/empty/error/hover/responsive breakpoint), and why (what you need confirmed). Tag it for escalation to the top-level session.
3. **Report this explicitly** in your own output and confidence-check — state that visual verification is pending external execution, not that the task is fully done. Per `confidence-check`'s rule on genuinely unreachable 100%: say so plainly, don't inflate the score.

## If you DO have a live connection (typically the top-level interactive session)

Use `mcp__playwright__*`: `browser_navigate`, `browser_tabs`, `browser_take_screenshot`, `browser_snapshot`, `browser_resize`, `browser_click`, `browser_type`, `browser_hover`, `browser_console_messages`, `browser_wait_for`, `browser_close`, `browser_file_upload` (for verifying file-upload UI — pass absolute file paths; omit `paths` to cancel an open file chooser).

1. **Get a live view of the app.** Navigate to the dev server URL with `browser_navigate`. Check `browser_tabs` first to avoid opening duplicate tabs.
2. **Screenshot after every meaningful visual change** using `browser_take_screenshot` (or `browser_snapshot` for a structured accessibility-tree view). Don't batch several changes and check once at the end.
3. **Capture every relevant state, not just the default render**: loading, empty, error, success, hover/focus. Drive the UI into each state first — `browser_click` / `browser_type` / `browser_hover` — and use `browser_wait_for` to let async state settle before checking.
4. **Check responsive behavior** with `browser_resize` for mobile/tablet/desktop viewports when the design is meant to adapt.
5. **Compare against the actual spec/design intent**, not your expectation of what the code should produce. Call out concrete mismatches: spacing, alignment, color, truncated text, overlapping elements, missing focus states.
6. **The rendered result is ground truth.** If code looks correct but the page shows a defect, trust the page — fix and recheck.
7. **Check `browser_console_messages`** when a visual bug might be a JS error rather than pure styling.
8. **Close the page/tab when done** with `browser_close`.
9. **Resolve any pending requests on the team board** left by subagents (per the protocol above) and post the result back so they can pick it up.

## Role-specific application
- **senior-frontend-dev / junior-frontend-dev**: request verification of your implementation before reporting a UI task fully done.
- **ui-ux-designer**: request verification of the actual current state before forming a final usability/accessibility opinion — real rendering can diverge from intent (CSS specificity, missed breakpoints).
- **product-owner**: request verification of the live feature in the acceptance-criteria state(s) before signing off — don't approve from a code diff alone.
- **qa-engineer**: request verification of the specific state/edge case under test for any UI-facing test case or bug fix — a passing assertion doesn't confirm the UI actually looks correct.
- **engineering-director**: when a deployed role posts a visual-verification request, do not resolve it yourself unless you've confirmed you have a live connection in this exact invocation — escalate it in your report back to whoever invoked you (so it reaches the top-level session) rather than letting it silently disappear from the chain.

## Interaction with confidence-check
A UI-related claim does not reach 100% confidence on code-reading alone. If you can perform the check yourself, do it before claiming confidence. If you can't (subagent with no connection), confidence on the visual aspect stays explicitly below 100% with the gap named, until someone with a working connection resolves it.

## Anti-patterns
- Faking or assuming a screenshot result instead of either performing it or explicitly flagging it as pending.
- Treating a screenshot taken before the last code change as still valid — recheck after every visual edit.
- Reporting "should render correctly" without ever actually checking.
- Retry-looping on a Playwright tool call that's already failed once in this session — it won't succeed on retry if the connection genuinely isn't there.
