from pathlib import Path

from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.metrics import AnswerRelevancyMetric
from deepeval_junit_reporter import assert_test_with_junit_report

# Report file path
REPORT_DIR = Path(__file__).resolve().parent / "test_reports"
REPORT_FILE = REPORT_DIR / "deepeval_results.xml"

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


def test_example():
    assert_test_with_junit_report(
        test_case,
        [correctness_metric, relevancy_metric],
        output_path=REPORT_FILE,
    )
