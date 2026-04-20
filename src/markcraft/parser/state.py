from __future__ import annotations


class FileWrapper:
    def __init__(
        self,
        lines,
        start_line: int = 1,
        start_offset: int = 0,
        line_start_offsets: list[int] | None = None,
        line_start_columns: list[int] | None = None,
    ):
        self.lines = lines if isinstance(lines, list) else list(lines)
        self.start_line = start_line
        self.start_offset = start_offset
        self._index = -1
        self._anchor = 0
        if line_start_offsets is not None and len(line_start_offsets) != len(self.lines):
            raise ValueError("line_start_offsets length must match lines length")
        if line_start_columns is not None and len(line_start_columns) != len(self.lines):
            raise ValueError("line_start_columns length must match lines length")

        if line_start_offsets is not None:
            self._line_start_offsets = line_start_offsets
        else:
            self._line_start_offsets = []
            offset = start_offset
            for line in self.lines:
                self._line_start_offsets.append(offset)
                offset += len(line)

        if line_start_columns is not None:
            self._line_start_columns = line_start_columns
        else:
            self._line_start_columns = [1] * len(self.lines)

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

    def line_start_offset(self, index: int | None = None):
        if index is None:
            index = self._index
        if index < 0 or index >= len(self.lines):
            return self.start_offset
        return self._line_start_offsets[index]

    def line_end_offset(self, index: int | None = None):
        if index is None:
            index = self._index
        if index < 0 or index >= len(self.lines):
            return self.start_offset
        return self._line_start_offsets[index] + len(self.lines[index])

    def line_end_column(self, index: int | None = None):
        if index is None:
            index = self._index
        if index < 0 or index >= len(self.lines):
            return 1
        return self._line_start_columns[index] + len(self.lines[index])

    def line_start_column(self, index: int | None = None):
        if index is None:
            index = self._index
        if index < 0 or index >= len(self.lines):
            return 1
        return self._line_start_columns[index]


class ParseBuffer(list):
    """List wrapper with parser-specific metadata fields."""

    def __init__(self, *args):
        super().__init__(*args)
        self.loose = False
