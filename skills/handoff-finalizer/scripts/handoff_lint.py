#!/usr/bin/env python3
"""Deterministic handoff checks.

This script intentionally stays conservative. It does not edit files and it does
not try to understand every project. It catches structural omissions, obvious
secret leaks, vague placeholders, and risky handoff patterns so an agent can
repair the document before relying on it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Finding:
    severity: str
    code: str
    line: int | None
    message: str
    fix: str

    def as_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "code": self.code,
            "line": self.line,
            "message": self.message,
            "fix": self.fix,
        }


SECRET_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"), "Redact the OpenAI-style API key."),
    ("openrouter_key", re.compile(r"\bsk-or-[A-Za-z0-9_-]{12,}\b"), "Redact the OpenRouter API key."),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"), "Redact the Anthropic API key."),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._-]{24,}\b", re.I), "Redact the bearer token."),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"), "Redact the JWT."),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"), "Remove the private key block."),
    ("password_assignment", re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s<>]{8,}"), "Replace the password value with <redacted>."),
]

REQUIRED_SECTIONS = {
    "goal": ("goal", "objective", "high-level goal"),
    "first_action": ("first action", "recommended next step"),
    "current_state": ("current state", "status at a glance"),
    "completed": ("completed", "completed work", "done"),
    "pending": ("not completed", "pending", "next steps", "unfinished"),
    "verification": ("verification", "verified", "checks ran", "last verification"),
    "risks": ("risk", "blocker", "warning", "things not to do", "security"),
}

VAGUE_PATTERNS = [
    re.compile(r"\b(mostly|probably|maybe|somehow|basically|just continue|continue working)\b", re.I),
    re.compile(r"\b(TODO|TBD|FIXME|unknown)\b", re.I),
]

DANGEROUS_PATTERNS = [
    (re.compile(r"\b0\.0\.0\.0:?(8317|3001)\b"), "Do not expose internal service ports publicly."),
    (re.compile(r"\b(8317|3001)\b.*\b(public|internet)\b", re.I), "Mark internal ports as private behind a reverse proxy."),
    (re.compile(r"(?i)\bMERCAPIC_API_SECRET\b.*\b(browser|frontend|client)\b"), "Do not expose shared server secrets to browser/frontend code."),
]

NEGATING_WORDS = (
    "do not",
    "don't",
    "never",
    "not ",
    "cannot",
    "can't",
)

PATH_PATTERN = re.compile(
    r"(?P<path>(?:[A-Za-z]:\\[^\n\r`\"'<>|]+|/[A-Za-z0-9_./@+ -]{3,}))"
)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def headings(text: str) -> list[str]:
    result: list[str] = []
    for line in text.splitlines():
        line = line.lstrip("\ufeff").strip()
        if line.startswith("#"):
            result.append(line.lstrip("#").strip().lower())
        elif re.match(r"^[A-Za-z][A-Za-z0-9 /&-]{2,60}:\s*$", line):
            result.append(line.rstrip(":").strip().lower())
    return result


def has_section(section_headings: Iterable[str], aliases: Iterable[str]) -> bool:
    lowered = list(section_headings)
    return any(any(alias in heading for alias in aliases) for heading in lowered)


def check_sections(text: str) -> list[Finding]:
    found = headings(text)
    findings: list[Finding] = []
    for key, aliases in REQUIRED_SECTIONS.items():
        if not has_section(found, aliases):
            severity = "critical" if key in {"goal", "first_action", "current_state"} else "warning"
            findings.append(
                Finding(
                    severity,
                    f"missing_{key}",
                    None,
                    f"Missing a recognizable {key.replace('_', ' ')} section.",
                    f"Add a concise section for {key.replace('_', ' ')}.",
                )
            )
    return findings


def check_secrets(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for code, pattern, fix in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                Finding("critical", f"secret_{code}", line_number(text, match.start()), "Possible plaintext secret detected.", fix)
            )
    return findings


def check_vague(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for pattern in VAGUE_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                Finding(
                    "warning",
                    "vague_or_placeholder",
                    line_number(text, match.start()),
                    f"Vague or placeholder wording: {match.group(0)!r}.",
                    "Replace with a concrete state, action, or explicitly mark as unknown with owner/next check.",
                )
            )
    return findings


def check_dangerous(text: str) -> list[Finding]:
    findings: list[Finding] = []
    line_starts = [0]
    for match in re.finditer("\n", text):
        line_starts.append(match.end())
    for pattern, fix in DANGEROUS_PATTERNS:
        for match in pattern.finditer(text):
            line_start = max(start for start in line_starts if start <= match.start())
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            context = text[line_start:line_end].lower()
            if any(word in context for word in NEGATING_WORDS):
                continue
            findings.append(
                Finding(
                    "critical",
                    "dangerous_boundary",
                    line_number(text, match.start()),
                    f"Potentially dangerous boundary or secret-placement statement: {match.group(0)!r}.",
                    fix,
                )
            )
    return findings


def check_inline_diff(text: str) -> list[Finding]:
    diff_markers = sum(1 for line in text.splitlines() if line.startswith(("+", "-", "@@")) and not line.startswith(("+++", "---")))
    if diff_markers > 80:
        return [
            Finding(
                "warning",
                "large_inline_diff",
                None,
                f"Handoff appears to contain a large inline diff ({diff_markers} diff-like lines).",
                "Reference the diff/commit/path instead of copying large patches into the handoff.",
            )
        ]
    return []


def normalize_path(raw: str) -> str:
    return raw.rstrip(".,);:]")


def check_paths(text: str) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for match in PATH_PATTERN.finditer(text):
        raw = normalize_path(match.group("path").strip())
        if raw in seen:
            continue
        seen.add(raw)
        if raw.startswith("/"):
            # POSIX paths are often remote-server paths; do not warn unless future checks can inspect that host.
            continue
        path = Path(raw)
        if not path.exists() and len(raw) > 8:
            findings.append(
                Finding(
                    "note",
                    "path_not_found_locally",
                    line_number(text, match.start()),
                    f"Referenced local path was not found from this machine: {raw}",
                    "If this is a remote path, label it as remote. If local, fix the path.",
                )
            )
    return findings


def check_length(text: str) -> list[Finding]:
    words = re.findall(r"\S+", text)
    if len(words) > 4000:
        return [
            Finding(
                "warning",
                "handoff_too_long",
                None,
                f"Handoff is long ({len(words)} token-ish words).",
                "Consider moving detailed provider notes or long references into appendix/reference files.",
            )
        ]
    return []


def audit(path: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[Finding] = []
    findings.extend(check_sections(text))
    findings.extend(check_secrets(text))
    findings.extend(check_dangerous(text))
    findings.extend(check_vague(text))
    findings.extend(check_inline_diff(text))
    findings.extend(check_paths(text))
    findings.extend(check_length(text))
    return findings


def verdict(findings: list[Finding]) -> str:
    if any(f.severity == "critical" for f in findings):
        return "FAIL"
    if any(f.severity == "warning" for f in findings):
        return "WARN"
    return "PASS"


def markdown_report(path: Path, findings: list[Finding]) -> str:
    result = verdict(findings)
    counts = {
        "critical": sum(1 for f in findings if f.severity == "critical"),
        "warning": sum(1 for f in findings if f.severity == "warning"),
        "note": sum(1 for f in findings if f.severity == "note"),
    }
    lines = [
        "# Handoff Audit Report",
        "",
        f"- Handoff: `{path}`",
        f"- Verdict: `{result}`",
        f"- Findings: {counts['critical']} critical, {counts['warning']} warning, {counts['note']} note",
        "",
    ]
    if not findings:
        lines.append("No deterministic findings.")
    else:
        lines.append("## Findings")
        lines.append("")
        for finding in findings:
            loc = f":{finding.line}" if finding.line else ""
            lines.append(f"- **{finding.severity.upper()} `{finding.code}`{loc}**: {finding.message}")
            lines.append(f"  Fix: {finding.fix}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a handoff markdown file.")
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--report", type=Path, help="Write a Markdown audit report.")
    args = parser.parse_args()

    if not args.handoff.exists():
        print(f"handoff_lint: file not found: {args.handoff}", file=sys.stderr)
        return 2

    findings = audit(args.handoff)
    result = {"verdict": verdict(findings), "findings": [finding.as_dict() for finding in findings]}

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(markdown_report(args.handoff, findings), encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Verdict: {result['verdict']}")
        if not findings:
            print("No deterministic findings.")
        for finding in findings:
            loc = f":{finding.line}" if finding.line else ""
            print(f"- [{finding.severity.upper()}] {finding.code}{loc}: {finding.message}")
            print(f"  Fix: {finding.fix}")
    return 1 if result["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
