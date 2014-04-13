from . import *

from midx.scanner import Scanner, parse_path


class TestPathParsing(TestCase):

    def test_various_parsing(self):

        self.assertEqual(parse_path('/prefix.1.postfix'), ('/prefix.', '.postfix', 1, None))
        self.assertEqual(parse_path('/prefix.001.postfix'), ('/prefix.', '.postfix', 1, 3))
        self.assertEqual(parse_path('/prefix.10.postfix'), ('/prefix.', '.postfix', 10, None))
        self.assertEqual(parse_path('/prefix.010.postfix'), ('/prefix.', '.postfix', 10, 3))