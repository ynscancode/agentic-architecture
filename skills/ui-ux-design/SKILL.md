---
name: ui-ux-design
description: Use when wireframing a new feature, reviewing UI for usability/accessibility issues, or specifying interaction states for devs to implement. Primary skill for the ui-ux-designer subagent.
---

# UI/UX Design

## Workflow
1. **Anchor to the existing design system** — reuse existing components, spacing, and patterns before proposing new ones.
2. **Spec all states**, not just the happy path: empty, loading, error, success, and edge cases (very long text, zero items, permission-denied).
3. **Accessibility pass** — color contrast, keyboard navigation, focus order, ARIA labeling for any new interactive element.
4. **Hand off as a spec**, not code: describe layout, component hierarchy, states, and interactions in enough detail that a frontend dev can implement without guessing.

## Accessibility checklist
- [ ] Sufficient color contrast (WCAG AA minimum)
- [ ] All interactive elements reachable/operable via keyboard
- [ ] Meaningful focus order and visible focus states
- [ ] Form inputs have associated labels
- [ ] Error messages are programmatically associated with their field

## Anti-patterns
- Don't introduce a new visual pattern when an existing one already solves the problem.
- Don't design only the happy path and leave error/empty states undefined.
