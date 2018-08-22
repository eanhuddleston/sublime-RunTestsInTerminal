import subprocess


class ItermExporter:
    def execute_shell_command(self, shell_command):
        applescript_command = """
        tell application "iTerm"
            tell current tab of current window
                tell the current session
                    set command to "{shell_command}"
                    write text command
                end tell
            end tell
        end tell
        """.format(shell_command=shell_command)
        self._execute_shell_command(applescript_command)

    def display_notification(self, message):
        # iTerm is only on OS X, so just use OS X's notification functionality
        applescript_command = """
        tell application "iTerm"
            display notification "{message}" with title "Tasty error"
        end tell
        """.format(message=message)
        self._execute_shell_command(applescript_command)

    def _execute_shell_command(self, command):
        subprocess.Popen(['osascript', '-e', command])
