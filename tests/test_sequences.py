from . import *

from midx.sequence import merge_sequences


class TestSequenceMerging(TestCase):

    def test_non_overlapping(self):

        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 20, 30, id=2)
        m = list(merge_sequences((a, b)))
        self.assertEqual(m, [
            ([], a),
            ([], b),
        ])

    def test_small_gap(self):

        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 12, 30, id=2)
        m = list(merge_sequences((a, b)))
        self.assertEqual(m, [
            ([], a),
            ([], b),
        ])

    def test_overlapping(self):

        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 5, 20, id=2)
        m = list(merge_sequences((a, b)))
        self.assertEqual(m, [
            ([b], Sequence('', '', 1, 20)),
        ])

    def test_touching(self):

        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 11, 20, id=2)
        m = list(merge_sequences((a, b)))
        self.assertEqual(m, [
            ([b], Sequence('', '', 1, 20)),
        ])

    def test_touching_one(self):
        # Adding a single new frame to the end.
        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 11, 11, id=None)
        m = list(merge_sequences((a, b)))
        self.assertEqual(m, [
            ([b], Sequence('', '', 1, 11)),
        ])

    def test_exact(self):

        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 1, 10, id=2)
        m = list(merge_sequences((a, b)))
        self.assertIs(m[0][0][0], b)
        self.assertEqual(m, [
            ([b], Sequence('', '', 1, 10)),
        ])

    def test_exact_one_is_new(self):

        a = Sequence('', '', 1, 10, id=1)
        b = Sequence('', '', 1, 10, id=None)
        m = list(merge_sequences((a, b)))
        self.assertIs(m[0][0][0], b)
        self.assertEqual(m, [
            ([b], Sequence('', '', 1, 10)),
        ])


