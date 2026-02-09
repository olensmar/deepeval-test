#!/usr/bin/env bash
# Run deepeval tests using the project venv (so deepeval_junit_reporter is found).
# One-time setup: .venv/bin/pip install -e ./deepeval_junit_reporter
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [[ ! -d .venv ]]; then
  echo "No .venv found. Create one, then: pip install -e ./deepeval_junit_reporter deepeval"
  exit 1
fi
.venv/bin/deepeval test run "$@"
