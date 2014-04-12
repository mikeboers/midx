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
def create_files_table(cur):
    cur.execute('''CREATE TABLE files (
        id INTEGER PRIMARY KEY,
        sequence_id INTEGER REFERENCES sequences(id) NOT NULL,
        'number' INTEGER NOT NULL,
        inode INTEGER NOT NULL,
        device INTEGER NOT NULL,
        size INTEGER NOT NULL,
        mtime INTEGER NOT NULL,
        ctime INTEGER NOT NULL,
        itime INTEGER NOT NULL, -- last index time
        checksum TEXT,
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

                cur.execute('SELECT id FROM sequences WHERE prefix = ? AND postfix = ?', [prefix, postfix])
                existing = set(row[0] for row in cur)

                if replace:
                    to_add = group
                else:
                    to_add = merge_sequences(itertools.chain(existing, group))

                for seq in to_add:
                    if seq.id is None:
                        cur.execute('''INSERT INTO sequences
                            (prefix, postfix, start, end, padding)
                            VALUES (?, ?, ?, ?, ?)
                        ''', [prefix, postfix, seq.start, seq.end, seq.padding])
                        seq.id = cur.lastrowid

                    for file_ in seq.files:
                        cur.execute('''INSERT INTO files
                            (sequence_id, 'number', inode, device, size, mtime, ctime, itime)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', [seq.id, file_.number, file_.inode, file_.device, file_.size, file_.mtime, file_.ctime, file_.itime])
                        file_.id = cur.lastrowid

                to_delete = existing.difference(seq.id for seq in to_add)
                if to_delete:
                    cur.executemany('''DELETE FROM sequences WHERE id = ?''', ([x] for x in to_delete))
