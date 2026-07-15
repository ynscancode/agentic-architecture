---
name: security-review
description: Use when reviewing code for vulnerabilities (OWASP top 10, injection, XSS, auth flaws), auditing dependencies, or assessing security impact of a design. Primary skill for the security-engineer subagent.
---

# Security Review

## Checklist (OWASP-aligned)
- [ ] Injection: SQL/command/template injection — parameterized queries, no string-concatenated commands/queries
- [ ] XSS: unescaped user input rendered in HTML/JS context
- [ ] AuthN/AuthZ: missing access checks, broken object-level authorization (can user A access user B's resource by changing an ID?)
- [ ] Secrets: credentials/tokens/keys committed to code or logs
- [ ] Deserialization: untrusted data deserialized without validation
- [ ] Dependencies: known CVEs in direct/transitive dependencies
- [ ] SSRF: server-side requests built from user-controlled URLs/hosts
- [ ] Data exposure: sensitive fields returned in API responses that don't need them

## Workflow
1. Read the diff/code with the checklist above as a lens, not as a vague "look for bugs" pass.
2. For each finding: confirm actual exploitability (can it be triggered by an attacker?) before flagging it as critical — don't inflate theoretical issues.
3. Prioritize by impact × exploitability, and give a concrete fix, not just a description of the problem.
4. Only assist with defensive review and authorized testing; decline destructive/offensive requests without clear authorization context.

## Output format
Finding — Severity (with reasoning) — Concrete fix.
