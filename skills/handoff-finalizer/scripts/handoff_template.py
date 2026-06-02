#!/usr/bin/env python3
"""Create a handoff skeleton with the sections the finalizer expects."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


TEMPLATE = """# {title}

Last updated: {timestamp}

## Goal

Write the future-session objective here.

## First Action

Write one immediate, executable step here.

## Current State

Describe what exists now. Separate verified facts from assumptions.

## Completed Work

- List work that was actually completed.

## Not Completed / Pending Work

- List work that still needs doing.

## Verification Evidence

- List commands/checks/results, or explicitly write `Not verified`.

## Decisions Made

- Record important choices and why.

## Risks / Blockers / Things Not To Do

- List safety risks, blockers, failed paths, and dangerous actions to avoid.

## Artifacts / Paths

- Add exact files, URLs, branches, commits, issues, or PRs.

## Sensitive Data Boundaries

- Name where secrets live, but never include secret values.

## Suggested Skills

- Add skills the next agent should use.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a handoff skeleton.")
    parser.add_argument("--title", default="Session Handoff")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    content = TEMPLATE.format(title=args.title, timestamp=datetime.now().isoformat(timespec="seconds"))
    args.output.write_text(content, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
