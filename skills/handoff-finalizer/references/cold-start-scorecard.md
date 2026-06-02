# Cold-Start Scorecard

Use this scorecard after a subagent reads only the handoff file.

## Required Subagent Answers

The subagent should correctly state:

1. Objective
2. Completed state
3. Pending state
4. First action
5. Files/URLs/commands to inspect first
6. Security risks and things not to do
7. Uncertainties or blockers

## Scoring

Score each category:

- `2`: correct and actionable
- `1`: partially correct or too vague
- `0`: wrong, missing, or dangerous

Suggested verdict:

- `PASS`: total score >= 12 and no category scores 0.
- `WARN`: total score >= 9 and no critical category is dangerous.
- `FAIL`: any dangerous answer, objective misunderstanding, completed/pending inversion, missing first action, or total score < 9.

Critical categories:

- Objective
- Completed state
- Pending state
- First action
- Security risks / things not to do

## Repair Rule

If the subagent misunderstands a critical category, repair the handoff and rerun the cold-start review. Do not accept a handoff that only the original session can understand.
