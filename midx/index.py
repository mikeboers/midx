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
        for sequence in Scanner().walk(root):
            self.broker.add_sequences([sequence], replace=True)

