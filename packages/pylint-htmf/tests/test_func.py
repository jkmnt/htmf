# based on tests from https://github.com/pylint-dev/pylint-django

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).parent

from pylint.testutils import FunctionalTestFile, LintModuleTest, lint_module_test

lint_module_test.PYLINTRC = HERE / "testing_pylint.rc"

sys.path += [str(p.absolute()) for p in (HERE, HERE / "../../", HERE / "functional")]


class PylintHtmfLintModuleTest(LintModuleTest):
    def __init__(self, test_file):
        super(PylintHtmfLintModuleTest, self).__init__(test_file)  # noqa
        self._linter.load_plugin_modules(["pylint_htmf"])
        self._linter.load_plugin_configuration()

    # copy of LintModuleTest w/o output compare.
    # Comparing exact output with .txt files is too much ceremony, just
    # Pass/FailMsg is enough
    def runTest(self) -> None:
        __tracebackhide__ = True  # pylint: disable=unused-variable
        modules_to_check = [self._test_file.source]
        self._linter.check(modules_to_check)
        expected_messages, expected_output = self._get_expected()
        actual_messages, actual_output = self._get_actual()
        assert expected_messages == actual_messages, self.error_msg_for_unequal_messages(actual_messages, expected_messages, actual_output)


def get_tests(input_dir="functional"):
    input_dir = HERE / input_dir

    suite = []
    for fname in input_dir.iterdir():
        if fname.name != "__init__.py" and fname.name.endswith(".py"):
            suite.append(FunctionalTestFile(str(input_dir.absolute()), str(fname.absolute())))

    return suite


TESTS = get_tests()
TESTS_NAMES = [t.base for t in TESTS]


@pytest.mark.parametrize("test_file", TESTS, ids=TESTS_NAMES)
def test_everything(test_file):
    # copied from pylint.tests.test_functional.test_functional
    lint_test = PylintHtmfLintModuleTest(test_file)
    lint_test.setUp()
    lint_test.setUp()
    lint_test.runTest()
