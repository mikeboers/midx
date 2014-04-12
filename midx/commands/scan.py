from midx.index import Index

from .main import command, argument

@command(
    argument('index'),
    argument('path', nargs='+'),
    help='scan recursively for files',
)
def scan(args):

    idx = Index(args.index)
    for path in args.path:
        idx.scan(path)

