# deepeval-test

Deepeval test project with JUnit XML report output via [deepeval_junit_reporter](./deepeval_junit_reporter/).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # or: .venv\Scripts\activate on Windows
pip install deepeval
pip install -e ./deepeval_junit_reporter
```

## Run tests

Use the project venv so the local reporter is found:

```bash
# Option 1: script (uses .venv automatically)
./run_tests.sh test_example.py

# Option 2: activate venv then run
source .venv/bin/activate
deepeval test run test_example.py
```

If you run `deepeval test run` **without** activating the venv (e.g. plain `deepeval` in PATH), the wrong Python may be used and you’ll get:  
`ImportError: cannot import name 'assert_test_with_junit_report' from 'deepeval_junit_reporter'`.
