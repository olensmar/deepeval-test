"""
JUnit-style XML report generation for deepeval test runs.

Drop-in: use assert_test_with_junit_report() instead of assert_test() to get
JUnit XML reports with minimal code. For custom flows, use write_junit_xml().
"""

from deepeval_junit_reporter.reporter import (
    assert_test_with_junit_report,
    write_junit_xml,
)

__all__ = ["assert_test_with_junit_report", "write_junit_xml"]
