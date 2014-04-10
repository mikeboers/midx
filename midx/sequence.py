
import collections

BaseSequence = collections.namedtuple('BaseSequence',
    ('prefix', 'postfix', 'start', 'end', 'padding', 'id')
)

class Sequence(BaseSequence):
    def __new__(cls, prefix, postfix, start, end, padding=None, id=None):
        return super(Sequence, cls).__new__(cls, prefix, postfix, start, end, padding, id)


def merge_overlapping(seqs):
    """Merge overlapping sequences.

    The prefix, postfix, and padding are assumed to be the same.

    """

    seqs = sorted(seqs, key=lambda s: s.start)
    if len(seqs) <= 1:
        return seqs

    merged = [seqs.pop(0)]
    last = None

    for seq in seqs:

        if seq.start <= merged[-1].end + 1:
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
