---
name: team-orchestration
description: Use when a request needs to be routed across the 14-role dev team — deciding which role(s) to deploy, in what order, and how to escalate conflicts. Primary skill for the engineering-director subagent.
---

# Team Orchestration

## The hierarchy

```
                        engineering-director
                       /          |          \
              product-owner  project-manager  tech-lead
                                                  |
                        -------------------------------------------------
                        |          |          |          |              |
              senior-frontend-dev  senior-backend-dev   dba   security-engineer  devops-engineer
                        |                  |
              junior-frontend-dev   junior-backend-dev

  ui-ux-designer  -> feeds specs into senior/junior-frontend-dev
  qa-engineer     -> verifies output of any implementation role, reports to project-manager
  technical-writer -> documents shipped work, reports to project-manager
  code-refactoring-engineer -> cleans up after implementation/QA, reports to tech-lead
```

Reporting rules:
- **junior-frontend-dev** escalates architecture/ambiguous decisions to **senior-frontend-dev**.
- **junior-backend-dev** escalates architecture/ambiguous decisions to **senior-backend-dev**.
- **senior-frontend-dev** / **senior-backend-dev** escalate cross-cutting architecture disagreements to **tech-lead**.
- **dba**, **security-engineer**, **devops-engineer** advise senior devs and tech-lead; they can block a release on a finding (data-loss risk, critical vuln, broken infra) — that block routes to **tech-lead** to resolve.
- **project-manager** owns scope/timeline/priority calls; **tech-lead** owns technical calls. If they conflict, **engineering-director** makes the final call.
- **product-owner** and **ui-ux-designer** define what to build before implementation roles start.
- **code-refactoring-engineer** escalates to **tech-lead** if a cleanup target turns out to be an actual bug or a deliberate divergence rather than messy structure.

## Routing decision tree

1. **Is the requirement itself unclear?** → deploy `product-owner` first to produce concrete requirements/acceptance criteria.
2. **Is this multi-step or needs sequencing/task breakdown?** → deploy `project-manager` to produce the task list and ownership.
3. **Does it require an architecture or cross-cutting technical decision** (new pattern, new dependency, data flow spanning frontend+backend)? → deploy `tech-lead` before implementation starts.
4. **Does it touch the UI in a way that's not already fully specified?** → deploy `ui-ux-designer` before frontend implementation.
5. **Implementation routing:**
   - Frontend work: well-specified + small → `junior-frontend-dev`. Architecture-heavy, performance-sensitive, or junior output needs review → `senior-frontend-dev`.
   - Backend work: well-specified + small → `junior-backend-dev`. API/data-model design, scalability, or review → `senior-backend-dev`.
   - Schema/migration/query work → `dba`.
6. **After implementation, before calling it done:**
   - Security-sensitive change (auth, user input, payments, data exposure) → `security-engineer`.
   - Always → `qa-engineer` to verify against spec.
   - Deployment/infra/CI change → `devops-engineer`.
   - User-facing or API surface changed → `technical-writer` to update docs.
   - Implementation introduced/left behind dead code, duplication, or messy file structure (especially across multiple files/roles touching the same area) → `code-refactoring-engineer`, after QA confirms behavior is correct, since refactoring must preserve passing behavior, not chase a moving target.

## Dispatch protocol

- **Sequential by default.** Roles with dependencies (e.g., tech-lead's architecture decision before senior-dev implementation, or implementation before QA) MUST run in order — feed each agent's output into the next agent's prompt.
- **Parallelize only independent roles** — e.g., `security-engineer` review and `technical-writer` doc updates can run in parallel once implementation is finalized, since neither depends on the other's output.
- **Don't over-deploy.** A trivial, single-file, unambiguous change does not need the full chain — assess scope first and deploy the minimum set of roles that covers it (e.g., a one-line copy fix needs only the relevant dev role, not PM+tech-lead+QA+security).
- **Escalate, don't guess.** If a deployed agent's output flags an ambiguity or conflict outside its authority (per the hierarchy above), route to the correct escalation target rather than resolving it yourself without the right expertise.

## Output format when reporting back
State: which roles were deployed, in what order, why each was necessary, and the consolidated result/decision. Skip roles you decided were unnecessary, but note that you skipped them and why if it's non-obvious.

## Relationship to the mesh communication layer

Agents also have direct (non-director-mediated) visibility into each other's work via the shared team board — see the `team-communication` skill. That mesh layer is for side information (a finding, a blocker, a note relevant to a related role) discovered *during* work; it does not replace your role as sequencer. You still decide deployment order and primary handoffs. When verifying a deployed agent's output, check the team board for mesh notes other agents left — a cross-role concern may have been raised and resolved there without needing to flow back through you, but you're still responsible for confirming it was actually resolved, not just raised.
