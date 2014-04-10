import itertools
import os
import re

from midx.brokers import get_broker
from midx.sequence import Sequence, merge_overlapping


sequence_num_re = re.compile(r'^(.+)(\d+)(\D*)$')


class Index(object):

    def __init__(self, url):
        self.broker = get_broker(url)

    def scan(self, root):

        root = os.path.abspath(root)
        count = 0

        for dir_path, dir_names, file_names in os.walk(root):

            dir_names[:] = [x for x in dir_names if not x.startswith('.')]

            single_sequences = []
            for file_name in sorted(file_names):
                m = sequence_num_re.match(file_name)
                if not m:
                    continue
                prefix, num, postfix = m.groups()
                padding = len(num) if num.startswith('0') else None
                num = int(num)
                single_sequences.append(Sequence(os.path.join(dir_path, prefix), postfix, num, num, padding))

            for key, grouped in itertools.groupby(single_sequences, lambda s: (s.prefix, s.postfix)):
                grouped = list(grouped)
                merged = merge_overlapping(grouped)
                self.broker.add(merged, replace=True)
                count += len(merged)

        return count
