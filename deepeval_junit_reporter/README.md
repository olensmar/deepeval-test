# deepeval-junit-reporter

JUnit-style XML report generation for [deepeval](https://github.com/confident-ai/deepeval) test runs. Reusable across projects so CI and reporting tools (Jenkins, GitLab CI, Azure Pipelines, etc.) can consume the same format.

## Installation

From a local checkout (e.g. alongside your deepeval project):

```bash
pip install -e /path/to/deepeval_junit_reporter
```

Or add to your project's `pyproject.toml`:

```toml
[tool.setuptools.package-dir]
# ...
[tool.setuptools.packages.find]
# ...

# If you use a monorepo or vendored lib:
# dependencies = ["deepeval", "deepeval-junit-reporter @ file:///${PROJECT_ROOT}/../deepeval_junit_reporter"]
```

## Usage

**Minimal (recommended):** use `assert_test_with_junit_report()` as a drop-in replacement for `assert_test()`:

```python
from pathlib import Path
from deepeval_junit_reporter import assert_test_with_junit_report

REPORT_FILE = Path(__file__).resolve().parent / "test_reports" / "deepeval_results.xml"

def test_example():
    assert_test_with_junit_report(
        test_case,
        [correctness_metric, relevancy_metric],
        output_path=REPORT_FILE,
    )
```

The test name in the XML is inferred from the calling function (`test_example`). Pass `test_name="..."` to override. Optional `verbose=False` disables the print of the report path.

**Custom flow:** call `write_junit_xml()` yourself after `assert_test()` if you need to handle timing or errors differently.

## API

- **`assert_test_with_junit_report(test_case, metrics, output_path, test_name=None, verbose=True, **kwargs)`**  
  Drop-in replacement for `assert_test()`. Runs the test, writes JUnit XML to `output_path` (always, including on failure), and re-raises on failure. `**kwargs` are passed to `assert_test` (e.g. `run_async`). Returns the resolved report path when the test passes.

- **`write_junit_xml(metrics, test_case, test_name, duration_seconds, output_path, assertion_error=None)`**  
  Writes a single JUnit XML file. Use when you need full control over timing and error handling. Returns the resolved `output_path`. Uses duck typing for `test_case` and `metrics` (compatible with deepeval's `LLMTestCase` and metric types).

## Requirements

- Python ≥ 3.9
- No runtime dependency on deepeval (your project provides it); the reporter only expects objects with the usual attributes (`input`, `actual_output`, `expected_output`, and metric `score` / `threshold` / `reason`).
