import datetime
import errno
import itertools
import os
import re
from unittest import TestCase as BaseTestCase

from midx.sequence import Sequence


_sandbox_time = datetime.datetime.utcnow()
def sandbox(*args):
    path = os.path.abspath(os.path.join(
        __file__,
        '..',
        'sandbox',
        _sandbox_time.isoformat('T'),
        *args
    ))
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return path


def _iter_touch_paths(patterns):
    if not patterns:
        return ['']
    chunk = patterns[0]
    the_rest = _iter_touch_paths(patterns[1:])
    if isinstance(chunk, basestring):
        return (chunk + x for x in the_rest)
    else:
        return (c + x for c, x in itertools.product(chunk, the_rest))


def touch(patterns, root=None):
    """Touch (or mkdir) a set of files specified by a list of patterns.

    A pattern is a list of strings or iterables, where the product of all
    iterables will be joined into a set of files to touch (or mkdir).

    """
    for pattern in patterns:
        for path in _iter_touch_paths(pattern):
            if root:
                path = os.path.join(root, path)
            dir_ = os.path.dirname(path)
            try:
                os.makedirs(dir_)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            if not path.endswith('/'):
                with open(path, 'a') as fh:
                    pass


class TestCase(BaseTestCase):

    @property
    def sandbox(self):
        return sandbox(self.id())

    def assertSearch(self, pattern, content):
        if not re.search(pattern, content):
            self.fail('\'%s\' does not match %r' % (pattern, content))