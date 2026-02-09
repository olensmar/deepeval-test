# Bridge so "from deepeval_junit_reporter import ..." works when run from project root
# (e.g. deepeval test run) without pip install -e. The real package lives in src/.
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_src = _here / "src"
_inner_init = _src / "deepeval_junit_reporter" / "__init__.py"

if _inner_init.exists():
    # Running from repo root: load inner package so we don't resolve to ourselves
    _key = "deepeval_junit_reporter"
    if _key in sys.modules and getattr(sys.modules[_key], "__file__", None) == str(_here / "__init__.py"):
        del sys.modules[_key]
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))
    from deepeval_junit_reporter import assert_test_with_junit_report, write_junit_xml
else:
    from deepeval_junit_reporter.reporter import assert_test_with_junit_report, write_junit_xml

__all__ = ["assert_test_with_junit_report", "write_junit_xml"]
