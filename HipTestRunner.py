from .hiptestrunner.test_runner import run_unit_tests
import sublime_plugin


class BaseTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print(
            "args:",
            "{} {} {}".format(
                self._file_with_path, self._current_line, self.test_type
            ),
        )
        run_unit_tests(
            self._file_with_path, self._current_line, self.test_type
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
