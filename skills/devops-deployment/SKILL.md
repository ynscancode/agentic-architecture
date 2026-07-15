---
name: devops-deployment
description: Use when setting up CI/CD pipelines, configuring deployments/infrastructure-as-code, setting up monitoring/alerting, or diagnosing production/infra issues. Primary skill for the devops-engineer subagent.
---

# DevOps / Deployment

## Workflow
1. **Prefer declarative, reproducible config** (IaC, pipeline-as-code) over manual one-off changes to infra.
2. **CI/CD** — pipeline should run tests/lint/build on every change; deploys should be gated on those passing, not run ahead of them.
3. **Monitoring** — for any new service/endpoint, ensure there's a way to observe it (logs, metrics, or an alert) before considering it production-ready.
4. **Incident diagnosis** — check logs/metrics for the actual failure signature before changing config; don't guess-and-restart as a first move.

## Risk gate (confirm before acting)
- [ ] Is this destructive or hard to reverse (deleting infra, force-pushing a deploy, dropping a queue)?
- [ ] Does it affect shared/production state, or just local/dev?
- [ ] If yes to either — surface the action and its blast radius to the user before proceeding, even if technically capable of doing it directly.

## Anti-patterns
- Don't bypass CI checks (--no-verify, skipping tests) to unblock a deploy without flagging it.
- Don't make manual changes to infra that should be captured in IaC — they get silently lost.
