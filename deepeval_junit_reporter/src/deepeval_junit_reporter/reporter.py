"""
Generate JUnit-style XML from deepeval test case and metric results.

Uses duck typing for test_case and metrics in write_junit_xml so it can be
used without deepeval in the same process. assert_test_with_junit_report
requires deepeval and is a drop-in wrapper around assert_test.
"""

import inspect
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def write_junit_xml(
    *,
    metrics: list,
    test_case: Any,
    test_name: str,
    duration_seconds: float,
    output_path: Path | str,
    assertion_error: Optional[BaseException] = None,
) -> Path:
    """
    Write JUnit-style XML results for reporting and CI integration.

    Compatible with deepeval LLMTestCase and metric objects. test_case is
    expected to have: input, actual_output, expected_output (optional).
    Each metric is expected to have: name (or __class__.__name__), score,
    threshold, reason (optional).

    Args:
        metrics: List of measured deepeval metrics (with score, threshold, reason).
        test_case: Test case object with input, actual_output, expected_output.
        test_name: Name of the test (e.g. "test_example").
        duration_seconds: Test duration in seconds.
        output_path: File path for the XML report (parent dirs created if needed).
        assertion_error: If set, emitted as a <failure> in the XML.

    Returns:
        The resolved output_path as Path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    # Properties: test case inputs/outputs for analysis
    properties = ET.SubElement(testsuite, "properties")
    for key, attr in [
        ("input", "input"),
        ("actual_output", "actual_output"),
        ("expected_output", "expected_output"),
    ]:
        value = getattr(test_case, attr, None) or ""
        value_str = str(value)[:500]
        ET.SubElement(properties, "property", name=key, value=value_str)

    testcase = ET.SubElement(
        testsuite,
        "testcase",
        {
            "name": test_name,
            "classname": test_name,
            "time": f"{duration_seconds:.3f}",
        },
    )

    # Metric details in system-out
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
        msg = str(assertion_error)[:500]
        failure = ET.SubElement(testcase, "failure", message=msg)
        failure.text = str(assertion_error)

    tree = ET.ElementTree(ET.Element("testsuites"))
    tree.getroot().append(testsuite)
    ET.indent(tree, space="  ", level=0)

    with open(output_path, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

    return output_path.resolve()


def assert_test_with_junit_report(
    test_case: Any,
    metrics: list,
    output_path: Path | str,
    test_name: Optional[str] = None,
    verbose: bool = True,
    **kwargs: Any,
) -> Path:
    """
    Drop-in replacement for deepeval.assert_test that also writes a JUnit XML report.

    Runs assert_test(test_case, metrics, **kwargs), measures duration, and in all
    cases writes the JUnit report to output_path (including on assertion failure).
    Passes through any kwargs to assert_test (e.g. run_async).

    Args:
        test_case: deepeval LLMTestCase (or compatible).
        metrics: List of deepeval metrics to evaluate.
        output_path: Path for the JUnit XML file (parent dirs created if needed).
        test_name: Name used in the XML (e.g. "test_example"). If None, inferred
                   from the caller's function name.
        verbose: If True, print the path where the report was written.
        **kwargs: Passed through to assert_test (e.g. run_async=True).

    Returns:
        The resolved output_path. Raises AssertionError if the test failed.
    """
    from deepeval import assert_test

    if test_name is None:
        frame = inspect.currentframe()
        if frame is not None and frame.f_back is not None:
            test_name = frame.f_back.f_code.co_name
        else:
            test_name = "test"

    output_path = Path(output_path)
    assertion_error = None
    start = time.perf_counter()
    try:
        assert_test(test_case, metrics, **kwargs)
    except AssertionError as e:
        assertion_error = e
        raise
    finally:
        duration = time.perf_counter() - start
        out_path = write_junit_xml(
            metrics=metrics,
            test_case=test_case,
            test_name=test_name,
            duration_seconds=duration,
            output_path=output_path,
            assertion_error=assertion_error,
        )
        if verbose:
            print(f"\nJUnit XML results written to: {out_path}")
    return out_path
