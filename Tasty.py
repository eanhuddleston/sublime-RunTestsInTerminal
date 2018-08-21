import sublime
import sublime_plugin

from .testrunner.test_runner import TestRunner


class BaseTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("Tasty.sublime-settings")
        config_per_test_suite = settings.get('config_per_test_suite', None)
        test_output_options = settings.get('test_output_options', None)

        print(
            "args:",
            "{} {} {}".format(
                self._file_with_path, self._current_line, self.test_type
            ),
        )

        print(
            "config:",
            "{} {}".format(config_per_test_suite, test_output_options),
        )
        TestRunner().run_unit_tests(
            self._file_with_path,
            self._current_line,
            self.test_type,
            config_per_test_suite,
            test_output_options,
        )

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
