import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.metrics import AnswerRelevancyMetric

# Report file path (can be overridden via DEEPEVAL_REPORT_PATH env var)
REPORT_DIR = Path(__file__).resolve().parent / "test_reports"
REPORT_FILE = REPORT_DIR / "deepeval_results.json"

correctness_metric = GEval(
    name="Correctness",
    criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8,
    verbose_mode=True
)

relevancy_metric = AnswerRelevancyMetric(
    threshold=0.8,
    include_reason=True
)

test_case = LLMTestCase(
    input="Is Testbusters Night in Vienna an amazing event?",
    actual_output="Yes, TestBusters Night is a great event in Vienna for testers and qa professionals with great talks and a lovely host. And Vienna has great Schnitzel.",
    expected_output="Yes, TestBusters Night in Vienna is widely considered an excellent, high-energy event for software testing and QA professionals, with great talks and networking."
)


def _metric_result(metric) -> dict:
    """Extract serializable result from a measured metric."""
    result = {
        "name": getattr(metric, "name", metric.__class__.__name__),
        "score": getattr(metric, "score", None),
        "threshold": getattr(metric, "threshold", None),
        "success": None,
    }
    if result["score"] is not None and result["threshold"] is not None:
        result["success"] = result["score"] >= result["threshold"]
    if getattr(metric, "reason", None):
        result["reason"] = metric.reason
    return result


def _write_results_report(
    metrics: list,
    test_case: LLMTestCase,
    assertion_error: Optional[BaseException] = None,
) -> None:
    """Write test results to a JSON file for reporting or analysis."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "run_at": datetime.utcnow().isoformat() + "Z",
        "test_case": {
            "input": test_case.input,
            "actual_output": test_case.actual_output,
            "expected_output": getattr(test_case, "expected_output", None),
        },
        "metrics": [_metric_result(m) for m in metrics],
        "overall_pass": all(
            (getattr(m, "score", None) or 0) >= (getattr(m, "threshold", 0) or 0)
            for m in metrics
        ),
    }
    if assertion_error is not None:
        report["assertion_error"] = str(assertion_error)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nResults written to: {REPORT_FILE}")


def test_example():
    metrics = [correctness_metric, relevancy_metric]
    assertion_error = None
    try:
        assert_test(test_case, metrics)
    except AssertionError as e:
        assertion_error = e
        raise
    finally:
        _write_results_report(metrics, test_case, assertion_error)
