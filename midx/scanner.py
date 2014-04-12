import itertools
import logging
import os
import re
import time

from midx.sequence import Sequence
from midx.file import File


log = logging.getLogger(__name__)

sequence_num_re = re.compile(r'^(.+)(\d+)([^0-9/]*)$')


class Scanner(object):

    def walk(self, root):
        """Walk a path and iter new :class:`.Sequence` objects populated with
        :class:`.File` objects."""

        for dir_path, dir_names, file_names in os.walk(root):

            # TODO: better directory filtering.
            dir_names[:] = [x for x in dir_names if not x.startswith('.')]

            sequence = None

            for file_name in sorted(file_names):

                path = os.path.join(dir_path, file_name)
                try:
                    stat = os.stat(path)
                except OSError:
                    log.exception('could not stat %r' % path)
                    continue

                m = sequence_num_re.match(path)
                if not m:
                    continue
                prefix, num, postfix = m.groups()
                padding = len(num) if num.startswith('0') else None
                num = int(num)

                if (
                    sequence is None or
                    sequence.prefix != prefix or
                    sequence.postfix != postfix or
                    sequence.end + 1 < num
                ):
                    if sequence is not None:
                        yield Sequence
                    sequence = Sequence(prefix, postfix, num, num, padding)

                sequence.end = num
                file_ = File(None, sequence, num,
                    stat.st_ino,
                    stat.st_dev,
                    stat.st_size,
                    stat.st_ctime,
                    stat.st_mtime,
                    time.time()
                )
                sequence.files.append(file_)

            if sequence is not None:
                yield sequence
