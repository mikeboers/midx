from . import *

from midx.sequence import merge_sequences


class TestSequenceMerging(TestCase):

    def test_non_overlapping(self):

        a = Sequence('', '', 1, 10)
        b = Sequence('', '', 20, 30)
        m = merge_sequences((a, b))
        self.assertEqual(m, [a, b])

    def test_small_gap(self):

        a = Sequence('', '', 1, 10)
        b = Sequence('', '', 12, 30)
        m = merge_sequences((a, b))
        self.assertEqual(m, [a, b])

    def test_overlapping(self):

        a = Sequence('', '', 1, 10)
        b = Sequence('', '', 5, 20)
        m = merge_sequences((a, b))
        self.assertEqual(m, [Sequence('', '', 1, 20)])

    def test_touching(self):

        a = Sequence('', '', 1, 10)
        b = Sequence('', '', 11, 20)
        m = merge_sequences((a, b))
        self.assertEqual(m, [Sequence('', '', 1, 20)])


