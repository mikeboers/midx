import itertools


class Sequence(object):

    def __init__(self, prefix, postfix, start, end, padding=None, id=None, files=None):
        self.prefix = prefix
        self.postfix = postfix
        self.start = start
        self.end = end
        self.padding = padding
        self.id = id
        self.files = [] if files is None else files

    def __repr__(self):
        return '<Sequence %r \'%s%%%sd%s\' from %d to %d; %d files>' % (
            self.id,
            self.prefix,
            '0%d' % self.padding if self.padding else '',
            self.postfix,
            self.start,
            self.end,
            len(self.files)
        )

    def is_matching(self, other):
        return (
            self.prefix == other.prefix and
            self.postfix == other.postfix
        )

    def is_identical(self, other):
        return (
            self.is_matching(other) and
            self.start == other.start and
            self.end == other.end
        )

    __eq__ = is_identical


def merge_sequences(seqs, is_sorted=False):

    """Merge overlapping sequences.

    Earlier sequences will be updated to include later sequences.

    If given ``is_sorted=True``, given sequences must only be iterable, and are
    assumed to be sorted by their prefix, postfix, and start index.

    Returns an interator of ``(dropped_sequences, updated_sequence)``. If a sequence
    was untouched, then ``dropped_sequences`` will be an empty list.

    """

    seqs = seqs if is_sorted else sorted(seqs, key=lambda s: (s.prefix, s.postfix, s.start))
    groups = itertools.groupby(seqs, lambda s: (s.prefix, s.postfix))

    for group_key, seqs in groups:
        current = None

        for seq in seqs:

            if current is not None:
                if seq.start <= current.end + 1:
                    current.end = seq.end
                    sources.append(seq)
                    continue
                else:
                    yield sources, current
                    current = None

            if current is None:
                current = seq
                sources = []

        if current is not None:
            yield sources, current
