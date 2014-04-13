import itertools
import logging
import os
import re
import time

from midx.sequence import Sequence


log = logging.getLogger(__name__)

sequence_num_re = re.compile(r'^(.+)(\d+)([^0-9/]*)$')


def parse_path(path):
    m = sequence_num_re.match(path)
    if not m:
        return
    prefix, num, postfix = m.groups()
    padding = len(num) if num.startswith('0') else None
    num = int(num)
    return prefix, postfix, num, padding


class Scanner(object):

    def walk(self, root):
        """Walk a path and iter new :class:`.Sequence` objects populated with
        :class:`.File` objects."""

        for dir_path, dir_names, file_names in os.walk(root):

            # TODO: better directory filtering.
            dir_names[:] = [x for x in dir_names if not x.startswith('.')]

            sequence = None

            for file_name in sorted(file_names):

                parsed = parse_path(os.path.join(dir_path, file_name))
                if not parsed:
                    continue
                prefix, postfix, num, padding = parsed

                if (
                    sequence is None or
                    sequence.prefix != prefix or
                    sequence.postfix != postfix or
                    sequence.end + 1 < num
                ):
                    if sequence is not None:
                        yield sequence
                    sequence = Sequence(prefix, postfix, num, num, padding)

                sequence.end = num

            if sequence is not None:
                yield sequence
