import re

from ..common import FileWrapper

NOSE_CLASS_REGEX = re.compile(r'class (\w*Tests)\(\w*\):')
NOSE_METHOD_REGEX = re.compile(r'def (test\w*)\(self\):')

RUN_NOSE_CLASS_PATTERN = "{module_path}:{class_name}"
RUN_NOSE_METHOD_PATTERN = "{module_path}:{class_name}.{method_name}"


class NoseUnitTestFinder:
    def __init__(self, filename_with_full_path, line_num):
        self.filename_with_full_path = filename_with_full_path
        self.file_wrapper = FileWrapper(filename_with_full_path, line_num)

    def get_class_test_command_path(self):
        class_name = self._get_class_name()
        if class_name is None:
            return None
        return RUN_NOSE_CLASS_PATTERN.format(
            module_path=self.filename_with_full_path, class_name=class_name
        )

    def get_unit_test_command_path(self):
        class_name = self._get_class_name()
        method_name = self._get_method_name()
        if class_name is None or method_name is None:
            return None
        return RUN_NOSE_METHOD_PATTERN.format(
            module_path=self.filename_with_full_path,
            class_name=class_name,
            method_name=method_name,
        )

    def _get_method_name(self):
        return self.file_wrapper.find_pattern_from_starting_line(
            NOSE_METHOD_REGEX
        )

    def _get_class_name(self):
        return self.file_wrapper.find_pattern_from_starting_line(
            NOSE_CLASS_REGEX
        )
