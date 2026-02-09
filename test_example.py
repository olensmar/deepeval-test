import time
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.metrics import AnswerRelevancyMetric

# Report file path
REPORT_DIR = Path(__file__).resolve().parent / "test_reports"
REPORT_FILE = REPORT_DIR / "deepeval_results.xml"

correctness_metric = GEval(
    name="Correctness",
    criteria="Determine if the 'actual output' is correct based on the 'expected output'.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.7,
    verbose_mode=True
)

relevancy_metric = AnswerRelevancyMetric(
    threshold=0.7,
    include_reason=True
)

test_case = LLMTestCase(
    input="Is Testbusters Night in Vienna an amazing event?",
    actual_output="Yes, TestBusters Night is a great event in Vienna for testers and qa professionals with great talks and a lovely host. And Vienna has great Schnitzel.",
    expected_output="Yes, TestBusters Night in Vienna is widely considered an excellent, high-energy event for software testing and QA professionals, with great talks and networking."
)


def _write_junit_xml(
    metrics: list,
    test_case: LLMTestCase,
    test_name: str,
    duration_seconds: float,
    assertion_error: Optional[BaseException] = None,
) -> None:
    """Write JUnit-style XML results for reporting and CI integration."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    failed = assertion_error is not None

    testsuite = ET.Element(
        "testsuite",
        {
            "name": test_name,
            "tests": "1",
            "failures": "1" if failed else "0",
            "errors": "0",
            "skipped": "0",
            "time": f"{duration_seconds:.3f}",
            "timestamp": timestamp,
        },
    )

    # System-out style block with test case and metric details for analysis
    properties = ET.SubElement(testsuite, "properties")
    for key, value in [
        ("input", test_case.input),
        ("actual_output", test_case.actual_output),
        ("expected_output", getattr(test_case, "expected_output", None) or ""),
    ]:
        ET.SubElement(properties, "property", name=key, value=str(value)[:500])

    testcase = ET.SubElement(
        testsuite,
        "testcase",
        {
            "name": test_name,
            "classname": test_name,
            "time": f"{duration_seconds:.3f}",
        },
    )

    # Metric results as system-out for tooling that supports it
    out_parts = []
    for m in metrics:
        name = getattr(m, "name", m.__class__.__name__)
        score = getattr(m, "score", None)
        thresh = getattr(m, "threshold", None)
        reason = getattr(m, "reason", None) or ""
        out_parts.append(f"[{name}] score={score} threshold={thresh}\n{reason}")
    if out_parts:
        sysout = ET.SubElement(testcase, "system-out")
        sysout.text = "\n---\n".join(out_parts)

    if assertion_error is not None:
        failure = ET.SubElement(testcase, "failure", message=str(assertion_error)[:500])
        failure.text = str(assertion_error)

    tree = ET.ElementTree(ET.Element("testsuites"))
    tree.getroot().append(testsuite)
    ET.indent(tree, space="  ", level=0)
    with open(REPORT_FILE, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    print(f"\nJUnit XML results written to: {REPORT_FILE}")


def test_example():
    metrics = [correctness_metric, relevancy_metric]
    assertion_error = None
    start = time.perf_counter()
    try:
        assert_test(test_case, metrics)
    except AssertionError as e:
        assertion_error = e
        raise
    finally:
        duration = time.perf_counter() - start
        _write_junit_xml(
            metrics, test_case, "test_example", duration, assertion_error
        )
