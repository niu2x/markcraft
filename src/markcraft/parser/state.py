from __future__ import annotations


class FileWrapper:
    def __init__(self, lines, start_line: int = 1):
        self.lines = lines if isinstance(lines, list) else list(lines)
        self.start_line = start_line
        self._index = -1
        self._anchor = 0

    def __next__(self):
        if self._index + 1 < len(self.lines):
            self._index += 1
            return self.lines[self._index]
        raise StopIteration

    def __iter__(self):
        return self

    def __repr__(self):
        return repr(self.lines[self._index + 1:])

    def get_pos(self):
        """Returns the current reading position for later restoration."""
        return self._index

    def set_pos(self, pos):
        """Sets the current reading position."""
        self._index = pos

    def anchor(self):
        """@deprecated use ``get_pos`` instead."""
        self._anchor = self.get_pos()

    def reset(self):
        """@deprecated use ``set_pos`` instead."""
        self.set_pos(self._anchor)

    def peek(self):
        if self._index + 1 < len(self.lines):
            return self.lines[self._index + 1]
        return None

    def backstep(self):
        if self._index != -1:
            self._index -= 1

    def line_number(self):
        return self.start_line + self._index


class ParseBuffer(list):
    """List wrapper with parser-specific metadata fields."""

    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
