import unittest

from markcraft.parser import FileWrapper


class TestFileWrapper(unittest.TestCase):
    def test_get_set_pos(self):
        lines = ["# heading\n", "somewhat interesting\n", "content\n"]
        wrapper = FileWrapper(lines)
        assert next(wrapper) == "# heading\n"
        anchor = wrapper.get_pos()
        assert next(wrapper) == "somewhat interesting\n"
        wrapper.set_pos(anchor)
        assert next(wrapper) == "somewhat interesting\n"

    def test_anchor_reset(self):
        lines = ["# heading\n", "somewhat interesting\n", "content\n"]
        wrapper = FileWrapper(lines)
        assert next(wrapper) == "# heading\n"
        wrapper.anchor()
        assert next(wrapper) == "somewhat interesting\n"
        wrapper.reset()
        assert next(wrapper) == "somewhat interesting\n"
