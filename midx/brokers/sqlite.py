import contextlib
import itertools
import sqlite3

from midx.sequence import Sequence, merge_overlapping


class SQLiteBroker(object):

    def __init__(self, path):
        self.path = path
        self.upgrade_schema()

    @contextlib.contextmanager
    def _conn(self):
        with sqlite3.connect(self.path) as conn:
            yield conn

    @contextlib.contextmanager
    def _cur(self):
        with self._conn() as conn:
            yield conn.cursor()

    def upgrade_schema(self):
        with self._cur() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS main (
                id INTEGER PRIMARY KEY,
                prefix TEXT NOT NULL,
                postfix TEXT NOT NULL,
                start INTEGER NOT NULL,
                end INTEGER NOT NULL,
                padding INTEGER
            )''')

    def add(self, sequences, replace=False):
        key = lambda s: (s.prefix, s.postfix)
        sequences = sorted(sequences, key=key)
        for (prefix, postfix), group in itertools.groupby(sequences, key=key):
            with self._cur() as cur:

                cur.execute('SELECT id, start, end, padding FROM main WHERE prefix = ? AND postfix = ?', [prefix, postfix])
                existing = [Sequence(prefix, postfix, start, end, padding, id_) for id_, start, end, padding in cur]
            
                if replace:
                    to_add = group
                else:
                    to_add = merge_overlapping(itertools.chain(existing, group))

                for seq in to_add:
                    if seq.id is None:
                        cur.execute('''INSERT INTO main
                            (prefix, postfix, start, end, padding)
                            VALUES (?, ?, ?, ?, ?)
                        ''', [prefix, postfix, seq.start, seq.end, seq.padding])

                to_delete = set(seq.id for seq in existing).difference(seq.id for seq in to_add)
                for id_ in to_delete:
                    cur.execute('''DELETE FROM main WHERE id = ?''', [id_])