import re
import subprocess

DEFAULT_TMUX_SESSION_NAME = '0'
DEFAULT_TMUX_WINDOW = 'testing'
PYTEST_COMMAND_TEMPLATE = (
    "'docker exec -it hipmunk_concurbot_1 pytest /hipmunk/{path_details} -s'"
)
NOSE_COMMAND_TEMPLATE = ("'runt {path_details}'")

CONCURBOT_TESTS_PATH = 'hipmunk/hello/concur/tests'
CONCURBOT_TESTS_PATH_REGEX = re.compile(CONCURBOT_TESTS_PATH + '/.*')
MONOLITH_TESTS_PATH = 'Hipmunk/tests'
MONOLITH_TESTS_PATH_REGEX = re.compile(MONOLITH_TESTS_PATH + '/.*')

PYTEST_CLASS_REGEX = re.compile(r'class (Test\w*)\(\w*\):')
GENERAL_PYTEST_TEST_DEF_REGEX = re.compile(r'def (test\w*)\(')
PYTEST_FUNCTION_REGEX = re.compile(r'^def (test\w*)\(')
PYTEST_METHOD_REGEX = re.compile(r'^\s{4}def (test\w*)\(')

NOSE_CLASS_REGEX = re.compile(r'class (\w*Tests)\(\w*\):')
NOSE_METHOD_REGEX = re.compile(r'def (test\w*)\(self\):')

RUN_PYTEST_CLASS_PATTERN = "{module_path}::{class_name}"
RUN_PYTEST_FUNCTION_PATTERN = "{module_path}::{function_name}"
RUN_PYTEST_METHOD_PATTERN = "{module_path}::{class_name}::{method_name}"

RUN_NOSE_CLASS_PATTERN = "{module_path}:{class_name}"
RUN_NOSE_METHOD_PATTERN = "{module_path}:{class_name}.{method_name}"


def run_unit_tests(file_with_path, line_num, test_type):
    codebase = _detect_codebase_using_file_location(file_with_path)
    if codebase == 'concurbot':
        run_cls = ConcurbotTestRunner
    elif codebase == 'monolith':
        run_cls = MonolithTestRunner
    run_cls().run_tests(file_with_path, line_num, test_type)


def _detect_codebase_using_file_location(file_with_path):
    if CONCURBOT_TESTS_PATH_REGEX.search(file_with_path):
        return 'concurbot'
    elif MONOLITH_TESTS_PATH_REGEX.search(file_with_path):
        return 'monolith'


class TestRunnerBase():
    def run_tests(self, file_with_path, line_num, test_type):
        self.file_wrapper = TestFileWrapper(file_with_path, line_num)

        self.file_name_with_path = (
            self.file_wrapper.filename_with_path_from_regex(
                self.codebase_tests_path_regex
            )
        )

        error_msg = None
        if test_type == 'all':
            path_details = self.codebase_tests_path
        if test_type == 'file':
            path_details = self.file_name_with_path
        if test_type == 'class':
            path_details = self._get_path_details_for_class()
            if path_details is None:
                error_msg = "No class found in: {}".format(
                    self.file_name_with_path
                )
        if test_type == 'unit':
            test_finder = self.test_finder_cls(self.file_wrapper)
            path_details = test_finder.get_path_details()
            if path_details is None:
                error_msg = "No unit test found in: {}".format(
                    self.file_name_with_path
                )

        if error_msg:
            TMUXWrapper.display_message(error_msg)
            return

        pytest_command = self.command_template.format(
            path_details=path_details
        )
        TMUXWrapper.send_command(pytest_command)

    def _get_path_details_for_class(self):
        class_name = (
            self.file_wrapper.find_pattern_from_starting_line(self.class_regex)
        )
        if class_name:
            return self.run_class_pattern.format(
                module_path=self.file_name_with_path,
                class_name=class_name,
            )
        return None


class NoseUnitTestFinder:
    def __init__(self, file_wrapper):
        self.file_wrapper = file_wrapper
        self.file_name_with_path = (
            self.file_wrapper.filename_with_path_from_regex(
                MONOLITH_TESTS_PATH_REGEX
            )
        )

    def get_path_details(self):
        return RUN_NOSE_METHOD_PATTERN(
            module_path=self.file_name_with_path,
            class_name=self._class_name,
            method_name=self._method_name,
        )

    @property
    def _method_name(self):
        return self.file_wrapper.find_pattern_from_starting_line(
            NOSE_METHOD_REGEX
        )

    @property
    def _class_name(self):
        return self.file_wrapper.find_pattern_from_starting_line(
            NOSE_CLASS_REGEX
        )


class PyTestUnitTestFinder:
    def __init__(self, file_wrapper):
        self.file_wrapper = file_wrapper
        self.file_name_with_path = (
            self.file_wrapper.filename_with_path_from_regex(
                CONCURBOT_TESTS_PATH_REGEX
            )
        )

    def get_path_details(self):
        self._find_closest_test_definition_from_cursor()
        test_details_dict = self._get_test_definition_details()
        if test_details_dict is None:
            return None
        if test_details_dict['test_type'] == 'function':
            return RUN_PYTEST_FUNCTION_PATTERN.format(
                module_path=self.file_name_with_path,
                function_name=test_details_dict['test_name'],
            )
        if test_details_dict['test_type'] == 'method':
            return RUN_PYTEST_METHOD_PATTERN.format(
                module_path=self.file_name_with_path,
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


class MonolithTestRunner(TestRunnerBase):
    codebase_tests_path = MONOLITH_TESTS_PATH
    codebase_tests_path_regex = MONOLITH_TESTS_PATH_REGEX
    command_template = NOSE_COMMAND_TEMPLATE
    test_finder_cls = NoseUnitTestFinder
    class_regex = NOSE_CLASS_REGEX
    run_class_pattern = RUN_NOSE_CLASS_PATTERN


class ConcurbotTestRunner(TestRunnerBase):
    codebase_tests_path = CONCURBOT_TESTS_PATH
    codebase_tests_path_regex = CONCURBOT_TESTS_PATH_REGEX
    command_template = PYTEST_COMMAND_TEMPLATE
    test_finder_cls = PyTestUnitTestFinder
    class_regex = PYTEST_CLASS_REGEX
    run_class_pattern = RUN_PYTEST_CLASS_PATTERN


class TestFileWrapper:
    def __init__(self, file_with_path, starting_line_num):
        self.file_with_path = file_with_path
        self.starting_line_num = starting_line_num
        self.current_line_num = starting_line_num
        self.text_from_last_line_read = ""

        with open(file_with_path) as f:
            self.lines = f.read().splitlines()

    def find_pattern_from_starting_line(self, regex):
        self.current_line_num = self.starting_line_num
        return self.find_pattern_from_current_line(regex)

    def find_pattern_from_current_line(self, regex):
        while True:
            text = self._read_line_and_decrement_position()
            if text is None:
                return None
            self.text_from_last_line_read = text
            match = regex.search(text)
            if match:
                return match.groups()[0]

    def _read_line_and_decrement_position(self):
        if self.current_line_num <= 0:
            return None
        text = self.lines[self.current_line_num - 1]
        self.current_line_num -= 1
        return text

    def filename_with_path_from_regex(self, regex):
        match = regex.search(self.file_with_path)
        if match:
            return match.group()
        return None


class TMUXWrapper:
    window_id = "{}:{}".format(DEFAULT_TMUX_SESSION_NAME, DEFAULT_TMUX_WINDOW)

    @classmethod
    def send_command(cls, command):
        cls._prepare_tmux()
        cls._execute_shell_command(
            "tmux send-keys -t {window_id} {command} c-m".format(
                window_id=cls.window_id, command=command
            )
        )

    @classmethod
    def display_message(cls, message):
        cls._prepare_tmux()
        cls._execute_shell_command("tmux display-message '{}'".format(message))

    @classmethod
    def _prepare_tmux(cls):
        cls._activate_window()
        cls._exit_scroll_mode()
        cls._clear_buffer_history()

    @classmethod
    def _activate_window(cls):
        cls._execute_shell_command(
            "tmux select-window -t {}".format(cls.window_id)
        )

    @classmethod
    def _exit_scroll_mode(cls):
        cls._execute_shell_command("tmux send-keys -t 'q'")

    @classmethod
    def _clear_buffer_history(cls):
        cls._execute_shell_command("tmux send-keys -R C-l \; clear-history")

    @classmethod
    def _execute_shell_command(cls, command):
        subprocess.call(command, shell=True)
