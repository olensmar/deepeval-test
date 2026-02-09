# deepeval-test

Deepeval test project with JUnit XML report output via [deepeval-junit-reporter](https://github.com/olensmar/deepeval-junit-reporter).

## Prerequisites

- Python ≥ 3.9
- An `OPENAI_API_KEY` environment variable (used by deepeval's LLM-based evaluation)
- A local clone of the [deepeval-junit-reporter](https://github.com/olensmar/deepeval-junit-reporter) repo

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # or: .venv\Scripts\activate on Windows
pip install deepeval
pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs `deepeval-junit-reporter` in editable mode from a sibling directory. Adjust the path in that file if your checkout is elsewhere.

## Run tests

Use the project venv so the reporter library is found:

```bash
# Option 1: helper script (uses .venv automatically)
./run_tests.sh test_example.py

# Option 2: activate venv then run
source .venv/bin/activate
deepeval test run test_example.py
```

JUnit XML results are written to `test_reports/deepeval_results.xml`.

If you run `deepeval test run` **without** activating the venv (e.g. plain `deepeval` in PATH), the wrong Python may be used and you'll get:
`ModuleNotFoundError: No module named 'deepeval_junit_reporter'`.
