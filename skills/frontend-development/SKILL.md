---
name: frontend-development
description: Use when designing component architecture, managing complex UI state, optimizing rendering/bundle performance, or reviewing junior frontend work. Primary skill for the senior-frontend-dev subagent.
---

# Frontend Development (Senior)

## Workflow
1. **Match existing patterns first** — check how the codebase already does state management, styling, and component composition before introducing anything new.
2. **Component design** — split by responsibility (presentation vs. logic vs. data fetching); keep state as local as possible, lift only when genuinely shared.
3. **Performance** — check for unnecessary re-renders, oversized bundles (lazy-load routes/heavy components), and unkeyed list renders before shipping.
4. **Verify in-browser** — for any UI change, run the dev server and exercise the golden path plus at least one edge case (empty state, error state, loading state) before calling it done.
5. **Reviewing juniors** — check for: pattern consistency, missing edge-case handling (empty/loading/error states), and unscoped refactors that exceeded the task.

## Anti-patterns
- Don't add a state-management library when local state/context suffices.
- Don't hand-roll something a project's existing UI library already provides.
- Don't claim a UI change works without actually viewing it (browser or dev tool), unless explicitly told testing isn't possible.
