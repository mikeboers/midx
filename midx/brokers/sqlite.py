import contextlib
import logging
import itertools
import sqlite3

from midx.sequence import Sequence, merge_sequences


log = logging.getLogger(__name__)


schema_migrations = []
def patch(func=None, name=None):
    if func is None:
        return functools.partial(patch, name=name)
    name = name or func.__name__
    name = name.strip('_')
    schema_migrations.append((name, func))
    return func

@patch
def create_sequences_table(cur):
    cur.execute('''CREATE TABLE sequences (
        id INTEGER PRIMARY KEY,
        prefix TEXT NOT NULL,
        postfix TEXT NOT NULL,
        start INTEGER NOT NULL,
        end INTEGER NOT NULL,
        padding INTEGER
    )''')

@patch
def create_file_stats_table(cur):
    cur.execute('''CREATE TABLE file_stats (
        id INTEGER PRIMARY KEY,
        sequence_id INTEGER REFERENCES sequences(id) NOT NULL,
        'number' INTEGER NOT NULL,
        inode INTEGER NOT NULL,
        device INTEGER NOT NULL,
        size INTEGER NOT NULL,
        mtime INTEGER NOT NULL,
        ctime INTEGER NOT NULL,
        UNIQUE (sequence_id, 'number')
    )''')

    
class SQLiteBroker(object):

    def __init__(self, path):
        self.path = path
        self.upgrade_schema()

    @contextlib.contextmanager
    def _conn(self):
        with sqlite3.connect(self.path) as conn:
            yield conn

    @contextlib.contextmanager
    def _cursor(self):
        with self._conn() as conn:
            yield conn.cursor()

    def upgrade_schema(self):

        with self._cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY,
                ctime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                name TEXT NOT NULL
            )''')
            cur.execute('SELECT name from schema_migrations')
            applied_patches = set(row[0] for row in cur)

        for name, func in schema_migrations:
            if name not in applied_patches:
                log.info('applying schema migration %s' % name)
                with self._cursor() as cur:
                    func(cur)
                    cur.execute('INSERT INTO schema_migrations (name) VALUES (?)', [name])

    def add_sequences(self, sequences, replace=False):

        key = lambda s: (s.prefix, s.postfix)
        sequences = sorted(sequences, key=key)
        for (prefix, postfix), group in itertools.groupby(sequences, key=key):
            with self._cursor() as cur:

                cur.execute('SELECT prefix, postfix, start, end, padding, id FROM sequences WHERE prefix = ? AND postfix = ?', [prefix, postfix])
                existing = [Sequence(*row) for row in cur]
                merged = list(merge_sequences(itertools.chain(existing, group)))

                for sources, seq in merged:

                    if seq.id is None:
                        cur.execute('''INSERT INTO sequences
                            (prefix, postfix, start, end, padding)
                            VALUES (?, ?, ?, ?, ?)
                        ''', [prefix, postfix, seq.start, seq.end, seq.padding])
                        seq.id = cur.lastrowid

                    # If any of the sources have changed the end.
                    elif any(src.end != seq.end for src in sources):
                        cur.execute('''UPDATE sequences SET end = ? WHERE id = ?''', [seq.end, seq.id])
                        # TODO: update any file pointers to sequences in sources

                if replace:
                    to_delete = set(s.id for s in existing).difference(seq.id for _, seq in merged)
                else:
                    to_delete = set()
                    for sources, seq in merged:
                        to_delete.update(src.id for src in sources if src.id is not None)

                if to_delete:
                    cur.executemany('''DELETE FROM sequences WHERE id = ?''', ([x] for x in to_delete))

    def iter_glob(self, prefix=None, postfix=None):
        where = []
        params = []
        if prefix:
            where.append('prefix GLOB ?')
            params.append(prefix)
        if postfix:
            where.append('postfix GLOB ?')
            params.append(postfix)
        clause = ('WHERE ' + ' AND '.join(where)) if where else ''
        with self._cursor() as cur:
            cur.execute('SELECT prefix, postfix, start, end, padding, id FROM sequences %s' % clause, params)
            for row in cur:
                yield Sequence(*row)
