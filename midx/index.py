import itertools
import os
import re

from midx.brokers import get_broker
from midx.scanner import Scanner


sequence_num_re = re.compile(r'^(.+)(\d+)(\D*)$')


class Index(object):

    def __init__(self, url):
        self.broker = get_broker(url)

    def scan(self, root):
        root = os.path.abspath(root)
        key = lambda s: (s.prefix, s.postfix)
        for key, sequences in itertools.groupby(Scanner().walk(root), key):
            self.broker.add_sequences(sequences, replace=True)

