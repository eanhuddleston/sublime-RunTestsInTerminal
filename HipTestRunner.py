from .hiptestrunner.test_runner import run_unit_tests
import sublime_plugin


class BaseTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # tmux_window_id = self._get_setting('tmux_window_id')
        # nose_command_template = self._get_setting('nose_command_template')
        # pytest_command_template = self._get_setting('pytest_command_template')

        print(
            "args:",
            "{} {} {}".format(
                self._file_with_path, self._current_line, self.test_type
            ),
        )
        run_unit_tests(
            self._file_with_path, self._current_line, self.test_type
        )

    def _get_setting(self, setting_name):
        setting_value = self.view.settings().get(setting_name, None)
        if setting_value:
            return setting_value.lower()
        return None

    @property
    def _file_with_path(self):
        return self.view.file_name()

    @property
    def _current_line(self):
        pnt = self.view.sel()[0].a
        line, _ = self.view.rowcol(pnt)
        return line + 1


class RunTestsCurrentUnitCommand(BaseTestCommand):
    test_type = 'unit'


class RunTestsCurrentClassCommand(BaseTestCommand):
    test_type = 'class'


class RunTestsCurrentFileCommand(BaseTestCommand):
    test_type = 'file'


class RunTestsAllCommand(BaseTestCommand):
    test_type = 'all'
