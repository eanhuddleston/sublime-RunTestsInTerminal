import re

from .command_exporters.tmux import TmuxExporter
from .command_exporters.iterm import ItermExporter
from .test_finders.nose import NoseUnitTestFinder
from .test_finders.pytest import PyTestUnitTestFinder


class TestRunner:
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
            if not self._does_config_apply_to_current_file(config):
                continue

            error_msg_template = None
            test_finder = self._get_test_finder(config)
            command_exporter = self._get_command_exporter()

            if self.test_type == 'suite':
                path_for_test_command = config['test_suite_path']
            elif test_type == 'file':
                path_for_test_command = self.filename_with_full_path
            elif test_type == 'class':
                path_for_test_command = (
                    test_finder.get_class_test_command_path()
                )
                if path_for_test_command is None:
                    error_msg_template = "No class found at current location"
            elif test_type == 'unit':
                path_for_test_command = (
                    test_finder.get_unit_test_command_path()
                )
                if path_for_test_command is None:
                    error_msg_template = (
                        "No unit test found at current location"
                    )

            if error_msg_template:
                self._send_error_msg(
                    command_exporter, error_msg_template, config
                )
                continue

            final_path_for_test_command = (
                self._remove_beginning_of_test_command_path_if_needed(
                    path_for_test_command, config
                )
            )
            test_command = self._create_test_command_for_framework(
                final_path_for_test_command, config
            )
            command_exporter.execute_shell_command(test_command)

    def _does_config_apply_to_current_file(self, config):
        match = re.search(
            config['test_suite_path'], self.filename_with_full_path
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

    def _get_command_exporter(self):
        output_options = self.test_output_options
        if 'tmux' in output_options:
            options = output_options['tmux']
            return TmuxExporter(
                session=options['session'], window=options['window']
            )
        elif 'iterm' in output_options:
            options = output_options['iterm']
            return ItermExporter()

    def _create_test_command_for_framework(
        self, trimmed_path_for_test_command, config
    ):
        command_template = config['command_template']
        return command_template.format(trimmed_path_for_test_command)

    def _remove_beginning_of_test_command_path_if_needed(
        self, test_command_path, config
    ):
        string_to_remove_from_beginning = config.get(
            'beginning_of_path_to_remove_for_test_command'
        )
        if string_to_remove_from_beginning is None:
            return test_command_path
        assert test_command_path.startswith(string_to_remove_from_beginning)
        return test_command_path[len(string_to_remove_from_beginning):]

    def _send_error_msg(self, command_exporter, error_msg_template, config):
        command_exporter.display_notification(
            error_msg_template.format(
                self._remove_beginning_of_test_command_path_if_needed(
                    self.filename_with_full_path, config
                )
            )
        )
