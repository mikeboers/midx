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
        return '<Sequence \'%s%%%sd%s\' from %d to %d; %d files>' % (
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

    If given ``sorted=True``, given sequences must only be iterable.
    The prefix, postfix, and padding are assumed to be the same.

    """

    seqs = seqs if is_sorted else sorted(seqs, key=lambda s: s.start)
    merged = []

    for seq in seqs:
        if merged and seq.start <= merged[-1].end + 1:
            last = merged.pop(-1)
            merged.append(Sequence(
                seq.prefix,
                seq.postfix,
                min(seq.start, last.start),
                max(seq.end, last.end),
                seq.padding,
            ))
        else:
            merged.append(seq)

    return merged
