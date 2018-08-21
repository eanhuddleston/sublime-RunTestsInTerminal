class FileWrapper:
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
