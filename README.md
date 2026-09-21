# DevSecOps Security Pipeline — Snyk in Practice

## Why this project exists

Most "security pipeline" demos stop at running a scanner and printing a pass/fail.
That's not really how security fits into DevSecOps — the value isn't the scan itself,
it's *where* the scan sits in the delivery process, *what* it's scanning, and *what
happens* when it finds something.

This repo is a hands-on lab built around **Snyk**, one of the tools I work with in my
current DevSecOps role, alongside Endor Labs and Veracode. Instead of reading docs in
isolation, this project puts Snyk in front of a real (if deliberately flawed) target —
outdated Python dependencies, a container image, and a small Terraform config — and
wires it into a GitHub Actions pipeline that behaves the way a production security gate
would: it scans on every push and pull request, consolidates results into a single
report, and **fails the build** when something serious is found.

The goal is shift-left security in miniature: catch dependency CVEs, container base-image
issues, and infrastructure misconfigurations *before* they reach a review, not after.

## What gets scanned

| Layer | Tool command | Target | What it catches |
|---|---|---|---|
| SCA (Software Composition Analysis) | `snyk test` | `app/requirements.txt` | Known CVEs in outdated Python packages |
| Container | `snyk container test` | Docker image built from `Dockerfile` | OS-level and base-image vulnerabilities |
| IaC | `snyk iac test` | `terraform/main.tf` | Misconfigurations (public S3 bucket, open security group) |

Each layer runs as its own job in the pipeline so failures are isolated and easy to
trace back to a cause.

## Architecture

```
push / PR
   │
   ├── SCA scan (Python deps)      ──┐
   ├── Container scan (Docker)     ──┼──► consolidated report.md ──► security gate
   └── IaC scan (Terraform)        ──┘         (posted to job summary)
```

The `scripts/generate_report.py` script pulls the raw JSON output from all three Snyk
scans, merges it into one Markdown report (posted directly to the GitHub Actions job
summary), and then re-runs in "gate" mode to decide whether the pipeline should fail —
currently anything `high` severity or above blocks the build.

## Repo structure

```
.
├── app/                   # Minimal Flask API — the scan target, not the point
│   ├── main.py
│   └── requirements.txt   # Intentionally outdated deps for Snyk SCA to flag
├── Dockerfile              # Older base image, target for container scanning
├── terraform/
│   └── main.tf             # Intentional misconfigs for Snyk IaC to flag
├── scripts/
│   └── generate_report.py  # Consolidates results + enforces the security gate
└── .github/workflows/
    └── security.yml        # The pipeline itself
```

## Setup

1. Clone the repo and open it in VS Code.
2. Create a free [Snyk](https://snyk.io) account and generate an API token.
3. In your GitHub repo settings, add the token as a secret named `SNYK_TOKEN`.
4. Push to `main` or open a pull request — the pipeline runs automatically.
5. Check the **job summary** on the workflow run for the consolidated report.

To run scans locally instead:

```bash
npm install -g snyk
snyk auth
snyk test --file=app/requirements.txt
snyk container test $(docker build -q .)
snyk iac test terraform/
```

## Status / roadmap

- [x] SCA scanning wired into CI
- [x] Container scanning wired into CI
- [x] IaC scanning wired into CI
- [x] Consolidated Markdown report + severity gate
- [ ] Fix the intentional vulnerabilities one by one, documenting the before/after
- [ ] Add a small HTML dashboard showing scan history over time
- [ ] Compare Snyk's findings against Endor Labs / Veracode on the same targets

## Notes

The vulnerabilities in this repo (outdated packages, old base image, open security
group, public S3 bucket) are **intentional** — this is a scanning target, not a
template for production code.
