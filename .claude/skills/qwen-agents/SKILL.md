---
name: qwen-agents
description: Dispatch and orchestrate local opencode Qwen3.8 Max subagents via the opencode CLI harness for ferrum-contracts issue/PR work — implementer, fix-round, and shepherd modes, with worktree isolation and the review loop. Qwen3.8 Max is the large-context tier (~983k context), suited to wide refactors and whole-subsystem audits. Use when the user asks Claude to spawn Qwen/qwen3.8-max agents on issues, PRs, review findings, or red CI.
---

# Qwen3.8 Max agents

Act as the orchestrator. Read and follow the shared workflow in
[the canonical skill](../../../.agents/skills/qwen-agents/SKILL.md), interpreting its Codex
orchestrator role as your Claude orchestrator role. Use the shared launcher and references;
do not duplicate them in this directory.

```bash
<ABS_REPO>/.agents/skills/qwen-agents/scripts/dispatch-agent.sh \
  --worktree <ABS_WORKER_WORKTREE> \
  --prompt-file <ABS_PROMPT_FILE>
```

`--effort` is accepted for CLI parity but ignored; never claim an effort level was applied.

Read the canonical skill before dispatch for validation, preflight, isolation, prompt construction, failure
handling, and verification. For implementer mode, read
[agent-brief.md](../../../.agents/skills/qwen-agents/references/agent-brief.md).
For fix-round or shepherd mode, also read
[continuation-brief.md](../../../.agents/skills/qwen-agents/references/continuation-brief.md).
Resolve all worker paths to absolute paths. Run each worker in its own background or long-lived
execution session and retain that session's identity. Never recursively invoke this skill from a
dispatched worker.
A worker that exits claiming it is "waiting on monitor" has ended its turn; treat every exit as a
completion and verify its state.

## Validation

Dispatched workers follow the "Validation" section of the implementer brief: they run the validator tests and `ci/validate.py --fetch-openapi` from a hash-pinned virtual environment outside the worktree, and treat CI results for the exact pushed head SHA as the source of truth. Pending,
skipped, unavailable, or earlier-head checks are not evidence that a change passed. The
controller owns post-push CI monitoring unless a worker is explicitly assigned a CI repair or
shepherd round, and never reports build/test success without matching remote evidence.

Include these validation commands and the remote CI confirmation requirement in every dispatch
prompt, including continuation prompts and any permitted nested delegation.
