import re
import subprocess

CONCURBOT_ALL_TESTS_PATH = 'hipmunk/hello/concur/tests'
PYTEST_COMMAND_TEMPLATE = (
    "'docker exec -it hipmunk_concurbot_1 pytest /hipmunk/{path_details} -s'"
)
TMUX_SESSION_NAME = '0'
TMUX_WINDOW = 'testing'

TMUX_WINDOW_ID = "{}:{}".format(TMUX_SESSION_NAME, TMUX_WINDOW)
TMUX_COMMAND_TEMPLATE = "tmux send-keys -t {window_id} {command} c-m".format(
    window_id=TMUX_WINDOW_ID, command='{command}'
)

CONCURBOT_REL_PATH_REGEX = re.compile('hipmunk/hello/concur/tests/.*')

PYTEST_CLASS_REGEX = re.compile('class (Test\w*)\(\w*\):')
GENERAL_PYTEST_TEST_DEF_REGEX = re.compile(r'def (test\w*)\(')
PYTEST_FUNCTION_REGEX = re.compile(r'^def (test\w*)\(')
PYTEST_METHOD_REGEX = re.compile(r'^\s{4}def (test\w*)\(')

RUN_PYTEST_CLASS_PATTERN = "{module_path}::{class_name}"
RUN_PYTEST_FUNCTION_PATTERN = "{module_path}::{function_name}"
RUN_PYTEST_METHOD_PATTERN = "{module_path}::{class_name}::{method_name}"


class PyTestTestRunner:
    def run_tests(self, file_with_path, line_num, test_type):
        self.file_wrapper = UnitTestFileWrapper(file_with_path, line_num)
        self.file_name_with_path = (
            self.file_wrapper.filename_from_hipmunk_dir_with_path
        )

        error_msg = None
        if test_type == 'all':
            path_details = CONCURBOT_ALL_TESTS_PATH
        if test_type == 'file':
            path_details = self.file_name_with_path
        if test_type == 'class':
            path_details = self._get_path_details_for_class()
            if path_details is None:
                error_msg = "No class found in: {}".format(
                    self.file_name_with_path
                )
        if test_type == 'unit':
            test_finder = PyTestUnitTestFinder(self.file_wrapper)
            path_details = test_finder.get_path_details()
            if path_details is None:
                error_msg = "No unit test found in: {}".format(
                    self.file_name_with_path
                )

        if error_msg:
            TMUXWrapper.display_message(error_msg)
            return

        pytest_command = PYTEST_COMMAND_TEMPLATE.format(
            path_details=path_details
        )
        TMUXWrapper.send_command(pytest_command)

    def _get_path_details_for_class(self):
        class_name = self.file_wrapper.find_pattern_from_starting_line(
            PYTEST_CLASS_REGEX
        )
        if class_name:
            return RUN_PYTEST_CLASS_PATTERN.format(
                module_path=self.file_name_with_path, class_name=class_name
            )
        return None


class PyTestUnitTestFinder:
    def __init__(self, file_wrapper):
        self.file_wrapper = file_wrapper
        self.file_name_with_path = (
            self.file_wrapper.filename_from_hipmunk_dir_with_path
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


class UnitTestFileWrapper:
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

    @property
    def filename_from_hipmunk_dir_with_path(self):
        match = CONCURBOT_REL_PATH_REGEX.search(self.file_with_path)
        return match.group()


class TMUXWrapper:
    @classmethod
    def send_command(self, command):
        self._prepare_tmux()
        self._execute_shell_command(
            TMUX_COMMAND_TEMPLATE.format(command=command)
        )

    @classmethod
    def display_message(self, message):
        self._prepare_tmux()
        self._execute_shell_command(
            "tmux display-message '{}'".format(message)
        )

    @classmethod
    def _prepare_tmux(self):
        self._activate_window()
        self._exit_scroll_mode()
        self._clear_buffer_history()

    @classmethod
    def _activate_window(self):
        self._execute_shell_command(
            "tmux select-window -t {}".format(TMUX_WINDOW_ID)
        )

    @classmethod
    def _exit_scroll_mode(self):
        self._execute_shell_command("tmux send-keys -t 'q'")

    @classmethod
    def _clear_buffer_history(self):
        self._execute_shell_command("tmux send-keys -R C-l \; clear-history")

    @classmethod
    def _execute_shell_command(self, command):
        subprocess.call(command, shell=True)
