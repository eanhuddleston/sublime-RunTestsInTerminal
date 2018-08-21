import re
import subprocess


class TestRunner():
    def run_unit_tests(
        self,
        filename_with_full_path,
        line_num,
        test_type,
        config_per_test_suite,
        test_output_options,
    ):
        self.filename_with_full_path = filename_with_full_path
        self.line_num = line_num
        self.test_type = test_type
        self.config_per_test_suite = config_per_test_suite
        self.test_output_options = test_output_options

        for config in self.config_per_test_suite:
            if not self._does_config_apply_to_users_current_file(config):
                continue

            error_msg_template = None
            test_finder = self._get_test_finder(config)
            test_exporter = self._get_test_exporter()

            if self.test_type == 'all':
                path_for_test_command = config['test_suite_path']
            elif test_type == 'file':
                path_for_test_command = self.filename_with_full_path
            elif test_type == 'class':
                path_for_test_command = (
                    test_finder.get_class_test_command_path()
                )
                if path_for_test_command is None:
                    error_msg_template = "No class found in: {}"
            elif test_type == 'unit':
                path_for_test_command = (
                    test_finder.get_unit_test_command_path()
                )
                if path_for_test_command is None:
                    error_msg_template = "No unit test found in: {}"

            if error_msg_template:
                self._send_error_msg(test_exporter, error_msg_template, config)
                continue

            trimmed_path_for_test_command = (
                self._remove_beginning_of_test_command_path(
                    path_for_test_command, config
                )
            )
            test_command = self._create_test_command_for_framework(
                trimmed_path_for_test_command, config
            )
            test_exporter.execute_shell_command(test_command)

    def _does_config_apply_to_users_current_file(self, config):
        match = re.search(
            config['test_suite_path'],
            self.filename_with_full_path,
        )
        if match:
            return True
        return False

    def _get_test_finder(self, config):
        test_framework = config.get('test_framework', None)
        if test_framework == 'pytest':
            finder_cls = PyTestUnitTestFinder
        elif test_framework == 'nose':
            finder_cls = NoseUnitTestFinder
        return finder_cls(self.filename_with_full_path, self.line_num)

    def _get_test_exporter(self):
        output_options = self.test_output_options
        if 'tmux' in output_options:
            options = output_options['tmux']
            return TMUXExporter(
                session=options['session'], window=options['window']
            )

    def _create_test_command_for_framework(
        self, trimmed_path_for_test_command, config
    ):
        command_template = config['command_template']
        return command_template.format(trimmed_path_for_test_command)

    def _remove_beginning_of_test_command_path(
        self, test_command_path, config
    ):
        string_to_remove_from_beginning = config[
            'beginning_of_path_to_remove_for_test_command'
        ]
        assert test_command_path.startswith(string_to_remove_from_beginning)
        return test_command_path[len(string_to_remove_from_beginning):]

    def _send_error_msg(self, test_exporter, error_msg_template, config):
        test_exporter.display_notification(error_msg_template.format(
            self._remove_beginning_of_test_command_path(
                self.filename_with_full_path, config
            )
        ))


NOSE_CLASS_REGEX = re.compile(r'class (\w*Tests)\(\w*\):')
NOSE_METHOD_REGEX = re.compile(r'def (test\w*)\(self\):')

RUN_NOSE_CLASS_PATTERN = "{module_path}:{class_name}"
RUN_NOSE_METHOD_PATTERN = "{module_path}:{class_name}.{method_name}"


class NoseUnitTestFinder:
    def __init__(self, filename_with_full_path, line_num):
        self.filename_with_full_path = filename_with_full_path
        self.file_wrapper = TestFileWrapper(filename_with_full_path, line_num)

    def get_class_test_command_path(self):
        class_name = self._get_class_name()
        if class_name is None:
            return None
        return RUN_NOSE_CLASS_PATTERN.format(
            module_path=self.filename_with_full_path,
            class_name=class_name
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


PYTEST_CLASS_REGEX = re.compile(r'class (Test\w*)\(\w*\):')
GENERAL_PYTEST_TEST_DEF_REGEX = re.compile(r'def (test\w*)\(')
PYTEST_FUNCTION_REGEX = re.compile(r'^def (test\w*)\(')
PYTEST_METHOD_REGEX = re.compile(r'^\s{4}def (test\w*)\(')

RUN_PYTEST_CLASS_PATTERN = "{module_path}::{class_name}"
RUN_PYTEST_FUNCTION_PATTERN = "{module_path}::{function_name}"
RUN_PYTEST_METHOD_PATTERN = "{module_path}::{class_name}::{method_name}"


class PyTestUnitTestFinder:
    def __init__(self, filename_with_full_path, line_num):
        self.filename_with_full_path = filename_with_full_path
        self.file_wrapper = TestFileWrapper(filename_with_full_path, line_num)

    def get_class_test_command_path(self):
        return RUN_PYTEST_CLASS_PATTERN.format(
            module_path=self.filename_with_full_path,
            class_name=self.file_wrapper.find_pattern_from_starting_line(
                PYTEST_CLASS_REGEX
            )
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


class TestFileWrapper:
    def __init__(self, filename_with_full_path, starting_line_num):
        self.filename_with_full_path = filename_with_full_path
        self.starting_line_num = starting_line_num
        self.current_line_num = starting_line_num
        self.text_from_last_line_read = ""

        with open(filename_with_full_path) as f:
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


class TMUXExporter:
    def __init__(self, session, window):
        self.window_id = "{}:{}".format(session, window)

    def execute_shell_command(self, shell_command):
        self._prepare_tmux()
        self._execute_shell_command(
            "tmux send-keys -t {window_id} '{shell_command}' Enter".format(
                window_id=self.window_id, shell_command=shell_command
            )
        )

    def display_notification(self, message):
        self._prepare_tmux()
        self._execute_shell_command("tmux display-message '{}'".format(message))

    def _prepare_tmux(self):
        self._activate_window()
        self._exit_scroll_mode()
        self._clear_current_line()
        self._clear_buffer_history()

    def _activate_window(self):
        self._execute_shell_command(
            "tmux select-window -t {}".format(self.window_id)
        )

    def _exit_scroll_mode(self):
        # Send a 'q' without an "Enter" following it, as a 'q' is all
        # that's necessary to exit vi-copy-mode, if we're in it.
        self._execute_shell_command("tmux send-keys -t {window_id} 'q'".format(
            window_id=self.window_id
        ))

    def _clear_current_line(self):
        self._execute_shell_command("tmux send-keys -t {window_id} C-c".format(
            window_id=self.window_id
        ))

    def _clear_buffer_history(self):
        self._execute_shell_command("tmux send-keys -t {window_id} -R \; clear-history".format(
            window_id=self.window_id
        ))

    def _execute_shell_command(cls, command):
        subprocess.call(command, shell=True)
