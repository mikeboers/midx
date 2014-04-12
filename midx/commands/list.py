from midx.index import Index

from .main import command, argument

@command(
    argument('index'),
    argument('prefix', nargs='?'),
    argument('postfix', nargs='?'),
    help='list sequences in an index',
    name='list'
)
def list_(args):

    idx = Index(args.index)
    for seq in idx.glob(args.prefix, args.postfix):
        print seq.printf_pattern

