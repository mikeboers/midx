
import collections

BaseSequence = collections.namedtuple('BaseSequence', ('prefix', 'postfix', 'start', 'end', 'padding'))

class Sequence(BaseSequence):
    def __new__(cls, prefix, postfix, start, end, padding=None):
        return super(Sequence, cls).__new__(cls, prefix, postfix, start, end, padding)


def merge_overlapping(seqs):
    """Merge overlapping sequences.

    The prefix, postfix, and padding are assumed to be the same.

    """

    seqs = sorted(seqs, key=lambda s: s.start)
    merged = []
    last = None

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
