---
name: antigravity-neon-agents
description: Dispatch and orchestrate local Gemini 4 Neon subagents via the standalone Google Antigravity agy CLI harness for ferrum-contracts issue/PR work — implementer, fix-round, shepherd, and read-only reviewer modes, with low/medium/high/xhigh thinking (default high), worktree isolation, and the review loop. Use when the user asks Claude to spawn Antigravity, agy, Gemini, or Gemini 4 Neon agents on issues, PRs, review findings, red CI, or an independent PR review.
---

# Antigravity Gemini 4 Neon agents

Act as the orchestrator. Read and follow the shared workflow in
[the canonical skill](../../../.agents/skills/antigravity-neon-agents/SKILL.md), interpreting its
Codex orchestrator role as your Claude orchestrator role. Use the shared launcher and references;
do not duplicate them in this directory.

```bash
<ABS_REPO>/.agents/skills/antigravity-neon-agents/scripts/dispatch-agent.sh \
  --worktree <ABS_WORKER_WORKTREE> \
  --prompt-file <ABS_PROMPT_FILE> \
  --effort <low|medium|high|xhigh>
```

The launcher pins `gemini-4-neon` and passes `--effort` straight through as `agy --effort`
(default `high`). Gemini 4 Neon publishes only `low`, `medium`, `high`, and `xhigh`; the launcher
rejects `max` and `ultra` rather than clamping, and there is no fast tier or `--fast` flag.

Read the canonical skill before dispatch for validation, preflight, isolation, prompt construction, failure
handling, and verification. For implementer mode, read
[agent-brief.md](../../../.agents/skills/antigravity-neon-agents/references/agent-brief.md).
For fix-round or shepherd mode, also read
[continuation-brief.md](../../../.agents/skills/antigravity-neon-agents/references/continuation-brief.md).
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
