import sublime
import sublime_plugin

from .test_runner.test_runner import TestRunner


class BaseTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings("RunTestsInTerminal.sublime-settings")
        config_per_test_suite = settings.get('config_per_test_suite', None)
        test_output_options = settings.get('test_output_options', None)

        if config_per_test_suite is None or test_output_options is None:
            print(
                "RunThisTest was not able to load your config settings; \
                please consult the README on github for where to place them."
            )
            return

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
            filename_with_full_path=self._file_with_path,
            line_num=self._current_line,
            test_type=self.test_type,
            config_per_test_suite=config_per_test_suite,
            test_output_options=test_output_options,
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


class RunTestsCurrentSuiteCommand(BaseTestCommand):
    test_type = 'suite'
