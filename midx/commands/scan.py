from midx.index import Index

from .main import command, argument

@command(
    argument('index'),
    argument('path', nargs='+'),
    help='scan recursively for files',
)
def scan(args):

    idx = Index(args.index)
    count = 0
    for path in args.path:
        count += idx.scan(path) or 0
    print count, 'added'

