from unittest import TestCase as BaseTestCase

from midx.sequence import Sequence


def sandbox(*args):
    path = os.path.abspath(os.path.join(
        __file__,
        '..',
        'sandbox',
        datetime.datetime.utcnow().isoformat('T'),
        *args
    ))
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return path


class TestCase(BaseTestCase):

    @property
    def sandbox(self):
        return sandbox(self.id())

    def assertSearch(self, pattern, content):
        if not re.search(pattern, content):
            self.fail('\'%s\' does not match %r' % (pattern, content))