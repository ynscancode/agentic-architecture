---
name: requirements-analysis
description: Use when translating a vague request into clear requirements, prioritizing backlog items, or writing user stories and acceptance criteria. Primary skill for the product-owner subagent.
---

# Requirements Analysis

## Workflow
1. **Restate the request** in your own words and identify what's actually ambiguous (not everything needs clarification — only genuine gaps).
2. **Write user stories** in the form: "As a [user], I want [capability], so that [outcome]."
3. **Define acceptance criteria** in given/when/then form, covering the golden path and at least the most likely edge cases.
4. **Prioritize** based on user/business value and dependency order, not just request order.

## Acceptance criteria template
- Given [context/precondition]
- When [action]
- Then [expected outcome]

## Anti-patterns
- Don't over-specify a simple, unambiguous request with unnecessary process.
- Don't silently resolve a genuine ambiguity by picking an interpretation — surface it.
- Don't write acceptance criteria that only cover the happy path.
