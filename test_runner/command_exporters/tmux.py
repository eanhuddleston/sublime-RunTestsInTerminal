import subprocess


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
        self._execute_shell_command(
            "tmux display-message '{}'".format(message)
        )

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
        self._execute_shell_command(
            "tmux send-keys -t {window_id} 'q'".format(
                window_id=self.window_id
            )
        )

    def _clear_current_line(self):
        self._execute_shell_command(
            "tmux send-keys -t {window_id} C-c".format(
                window_id=self.window_id
            )
        )

    def _clear_buffer_history(self):
        self._execute_shell_command(
            "tmux send-keys -t {window_id} -R \; clear-history".format(
                window_id=self.window_id
            )
        )

    def _execute_shell_command(cls, command):
        subprocess.call(command, shell=True)
