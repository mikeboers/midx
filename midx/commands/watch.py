import sys
import time
import logging

import midx.notify
from midx.index import Index
from midx.commands.main import command, argument
from midx.scanner import parse_path


log = logging.getLogger(__name__)


@command(
    argument('index'),
    argument('path', nargs='+'),
    help='watch paths for updates',
)
def watch(args):
    idx = Index(args.index)
    for path in midx.notify.iter_modified_files(args.path):
        log.info(path)
        idx.add_path(path)
