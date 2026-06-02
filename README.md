# Zihao's Personal Development Skills

This repository stores personal Codex skills: reusable workflows, checks, and bundled scripts that help future sessions continue work with less context loss.

## Available Skills

### Handoff Finalizer

Path: `skills/handoff-finalizer`

`handoff-finalizer` creates, audits, repairs, and validates handoff documents for future Codex sessions or subagents. Its purpose is to make sure a new session can understand the real current state of a project, the first action to take, what has already been verified, and which security boundaries must not be crossed.

Use it when you need to:

- Preserve the current session for a future agent or chat.
- Generate a continuation or context-transfer document.
- Audit an existing handoff for missing state, vague next steps, or unsafe instructions.
- Repair a handoff until another cold-start agent can understand it.
- Keep secrets out of handoff files.

The skill focuses on practical continuation quality, not just summarization. A good handoff should include a clear goal, one concrete first action, current state, completed work, pending work, verification evidence, risks, artifacts, and sensitive data boundaries.

## What It Includes

- `SKILL.md`: the main Codex skill instructions and workflow.
- `agents/openai.yaml`: UI metadata for the skill.
- `references/rubric.md`: detailed audit rubric and severity rules.
- `references/eval-cases.md`: mutation/evaluation cases for validating the skill.
- `references/cold-start-scorecard.md`: criteria for judging whether a fresh agent understood the handoff.
- `scripts/handoff_template.py`: creates a handoff skeleton.
- `scripts/handoff_lint.py`: deterministic linter for required sections, secret patterns, vague placeholders, and dangerous boundary statements.
- `scripts/handoff_mutation_eval.py`: mutation checks that verify the linter catches common handoff failures.

## Safety Boundaries

Handoff files should never contain plaintext passwords, API keys, OAuth tokens, JWTs, private keys, full environment files, or other secrets.

The linter is advisory. It catches common failures, but final judgment still needs an agent or human to verify project-specific facts and security context.

## Current Status

The initial version of `handoff-finalizer` was validated with:

- Python syntax checks for bundled scripts.
- Deterministic handoff linting.
- Mutation regression checks.
- Secret-pattern scanning.
- Cold-start subagent review on a real Alibaba Cloud ECS + CLIProxyAPI handoff.
