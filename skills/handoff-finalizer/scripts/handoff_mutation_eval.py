#!/usr/bin/env python3
"""Run simple mutation tests against handoff_lint.py.

The goal is not exhaustive testing. It catches regressions where the linter no
longer detects critical handoff failures such as missing first action, leaked
secrets, or unsafe public internal ports.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from collections.abc import Callable
from pathlib import Path

import handoff_lint


@dataclass
class MutationCase:
    name: str
    expected: str
    mutate: Callable[[str], str]
    required_codes: tuple[str, ...]


def remove_first_action(text: str) -> str:
    updated = re.sub(
        r"(?ims)^## First Action\s+.*?(?=^## |\Z)",
        "",
        text,
        count=1,
    )
    updated = re.sub(
        r"(?ims)^First Action:\s+.*?(?=^[A-Za-z][A-Za-z0-9 /&-]{2,60}:\s*$|^## |\Z)",
        "",
        updated,
        count=1,
    )
    return updated


def inject_secret(text: str) -> str:
    fake_key = "sk-" + "proj-" + "abcdefghijklmnopqrstuvwxyz123456"
    return text + f"\n\n## Temporary Bad Example\n\nAPI key: {fake_key}\n"


def expose_internal_port(text: str) -> str:
    return text + "\n\n## Temporary Bad Example\n\nOpen 0.0.0.0:8317 to the public internet.\n"


def frontend_secret(text: str) -> str:
    return text + "\n\n## Temporary Bad Example\n\nPut MERCAPIC_API_SECRET in frontend JavaScript.\n"


CASES = [
    MutationCase("remove_first_action", "FAIL", remove_first_action, ("missing_first_action",)),
    MutationCase("inject_secret", "FAIL", inject_secret, ("secret_openai_key",)),
    MutationCase("expose_internal_port", "FAIL", expose_internal_port, ("dangerous_boundary",)),
    MutationCase("frontend_secret", "FAIL", frontend_secret, ("dangerous_boundary",)),
]


def run_case(source: Path, case: MutationCase, out_dir: Path) -> dict[str, object]:
    text = source.read_text(encoding="utf-8", errors="replace")
    mutated = case.mutate(text)
    target = out_dir / f"{case.name}.md"
    target.write_text(mutated, encoding="utf-8")
    findings = handoff_lint.audit(target)
    actual = handoff_lint.verdict(findings)
    codes = {finding.code for finding in findings}
    passed = actual == case.expected and all(code in codes for code in case.required_codes)
    return {
        "name": case.name,
        "passed": passed,
        "expected": case.expected,
        "actual": actual,
        "required_codes": list(case.required_codes),
        "found_codes": sorted(codes),
        "file": str(target),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mutation tests for a handoff file.")
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep", action="store_true", help="Keep mutated files.")
    args = parser.parse_args()

    if not args.handoff.exists():
        print(f"handoff_mutation_eval: file not found: {args.handoff}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="handoff-mutations-") as tmp:
        out_dir = Path(tmp)
        results = [run_case(args.handoff, case, out_dir) for case in CASES]
        all_passed = all(result["passed"] for result in results)
        payload = {"verdict": "PASS" if all_passed else "FAIL", "cases": results}

        if args.keep:
            keep_dir = args.handoff.parent / "handoff-mutation-artifacts"
            keep_dir.mkdir(exist_ok=True)
            for result in results:
                src = Path(str(result["file"]))
                dst = keep_dir / src.name
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                result["file"] = str(dst)

        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"Mutation Verdict: {payload['verdict']}")
            for result in results:
                status = "PASS" if result["passed"] else "FAIL"
                print(f"- {status} {result['name']}: expected {result['expected']}, got {result['actual']}")
                print(f"  Required: {', '.join(result['required_codes'])}")
                print(f"  Found: {', '.join(result['found_codes'])}")
        return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
