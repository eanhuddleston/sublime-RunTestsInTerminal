import re

from ..common import FileWrapper

PYTEST_CLASS_REGEX = re.compile(r'class (Test\w*)\(?\w*\)?:')
GENERAL_PYTEST_TEST_DEF_REGEX = re.compile(r'def (test\w*)\(')
PYTEST_FUNCTION_REGEX = re.compile(r'^def (test\w*)\(')
PYTEST_METHOD_REGEX = re.compile(r'^\s{4}def (test\w*)\(')

RUN_PYTEST_CLASS_PATTERN = "{module_path}::{class_name}"
RUN_PYTEST_FUNCTION_PATTERN = "{module_path}::{function_name}"
RUN_PYTEST_METHOD_PATTERN = "{module_path}::{class_name}::{method_name}"


class PyTestUnitTestFinder:
    def __init__(self, filename_with_full_path, line_num):
        self.filename_with_full_path = filename_with_full_path
        self.file_wrapper = FileWrapper(filename_with_full_path, line_num)

    def get_class_test_command_path(self):
        class_name = self.file_wrapper.find_pattern_from_starting_line(
            PYTEST_CLASS_REGEX
        )
        if class_name is None:
            return None

        return RUN_PYTEST_CLASS_PATTERN.format(
            module_path=self.filename_with_full_path, class_name=class_name
        )

    def get_unit_test_command_path(self):
        self._find_closest_test_definition_from_cursor()
        test_details_dict = self._get_test_definition_details()
        if test_details_dict is None:
            return None
        if test_details_dict['test_type'] == 'function':
            return RUN_PYTEST_FUNCTION_PATTERN.format(
                module_path=self.filename_with_full_path,
                function_name=test_details_dict['test_name'],
            )
        if test_details_dict['test_type'] == 'method':
            return RUN_PYTEST_METHOD_PATTERN.format(
                module_path=self.filename_with_full_path,
                class_name=test_details_dict['class_name'],
                method_name=test_details_dict['test_name'],
            )

    def _find_closest_test_definition_from_cursor(self):
        self.file_wrapper.find_pattern_from_starting_line(
            GENERAL_PYTEST_TEST_DEF_REGEX
        )

    def _get_test_definition_details(self):
        text = self.file_wrapper.text_from_last_line_read
        match = PYTEST_FUNCTION_REGEX.search(text)
        if match:
            return dict(test_type='function', test_name=match.groups()[0])
        match = PYTEST_METHOD_REGEX.search(text)
        if match:
            return dict(
                test_type='method',
                test_name=match.groups()[0],
                class_name=self.file_wrapper.find_pattern_from_current_line(
                    PYTEST_CLASS_REGEX
                ),
            )
        return None
