#!/usr/bin/env python3
"""
Consolidates Snyk JSON scan output (SCA, container, IaC) into a single
Markdown report and, optionally, acts as a pipeline gate — exiting non-zero
if any issue at or above --fail-on severity is found.

Usage:
    python generate_report.py --input-dir results --output report.md
    python generate_report.py --input-dir results --gate --fail-on high
"""

import argparse
import json
import sys
from pathlib import Path

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

SCAN_FILES = {
    "sca-results": "SCA (Python dependencies)",
    "container-results": "Container (Docker image)",
    "iac-results": "IaC (Terraform)",
}


def find_result_files(input_dir: Path) -> dict:
    """Map scan label -> parsed JSON, searching artifact subfolders."""
    found = {}
    for key, label in SCAN_FILES.items():
        matches = list(input_dir.rglob(f"{key}.json"))
        if not matches:
            continue
        try:
            found[label] = json.loads(matches[0].read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(f"warning: could not read {matches[0]}: {exc}", file=sys.stderr)
    return found


def extract_issues(data: dict) -> list:
    """Snyk's JSON shape varies a bit by scan type; normalize what we need."""
    issues = data.get("vulnerabilities") or data.get("infrastructureAsCodeIssues") or []
    normalized = []
    for issue in issues:
        normalized.append(
            {
                "title": issue.get("title", "Untitled issue"),
                "severity": issue.get("severity", "low"),
                "package": issue.get("packageName") or issue.get("resourceType", "n/a"),
                "id": issue.get("id", "n/a"),
            }
        )
    return normalized


def build_report(results: dict) -> tuple:
    lines = ["# Security Scan Report", ""]
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    all_issues = []

    for label, data in results.items():
        issues = extract_issues(data)
        all_issues.extend(issues)
        lines.append(f"## {label}")
        if not issues:
            lines.append("No issues found. ✅")
            lines.append("")
            continue

        lines.append("| Severity | Issue | Package/Resource | ID |")
        lines.append("|---|---|---|---|")
        for issue in sorted(
            issues, key=lambda i: SEVERITY_ORDER.get(i["severity"], 0), reverse=True
        ):
            severity_counts[issue["severity"]] = severity_counts.get(issue["severity"], 0) + 1
            lines.append(
                f"| {issue['severity'].upper()} | {issue['title']} | "
                f"{issue['package']} | {issue['id']} |"
            )
        lines.append("")

    lines.insert(
        2,
        f"**Summary:** {severity_counts['critical']} critical, "
        f"{severity_counts['high']} high, {severity_counts['medium']} medium, "
        f"{severity_counts['low']} low\n",
    )

    return "\n".join(lines), all_issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("report.md"))
    parser.add_argument("--gate", action="store_true", help="Exit non-zero if the threshold is met")
    parser.add_argument("--fail-on", default="high", choices=SEVERITY_ORDER.keys())
    args = parser.parse_args()

    results = find_result_files(args.input_dir)
    if not results:
        print("No Snyk result files found — nothing to report.", file=sys.stderr)
        if args.gate:
            sys.exit(0)
        return

    report, issues = build_report(results)

    if not args.gate:
        args.output.write_text(report)
        print(f"Report written to {args.output}")
        return

    threshold = SEVERITY_ORDER[args.fail_on]
    blocking = [i for i in issues if SEVERITY_ORDER.get(i["severity"], 0) >= threshold]
    if blocking:
        print(f"Security gate FAILED: {len(blocking)} issue(s) at or above '{args.fail_on}'.")
        for issue in blocking:
            print(f"  - [{issue['severity'].upper()}] {issue['title']} ({issue['package']})")
        sys.exit(1)

    print(f"Security gate PASSED: no issues at or above '{args.fail_on}'.")


if __name__ == "__main__":
    main()
