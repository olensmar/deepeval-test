from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.metrics import AnswerRelevancyMetric

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
    actual_output="Yes, TestBusters Night is a great event for testers and qa professionals with great talks and a lovely host.",
    expected_output="Yes, TestBusters Night in Vienna is widely considered an excellent, high-energy event for software testing and QA professionals, with great talks and networking."
)

evaluate([test_case], [correctness_metric, relevancy_metric])