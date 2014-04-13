import sys
import time
import logging
from Queue import Queue, Empty

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from midx.index import Index
from midx.commands.main import command, argument
from midx.scanner import parse_path


log = logging.getLogger(__name__)


class EventHandler(FileSystemEventHandler):

    def __init__(self, queue):
        super(EventHandler, self).__init__()
        self.queue = queue
    
    def on_created(self, e):
        # e -> <FileCreatedEvent: src_path=/Users/mikeboers/fi/dev/midx/sandbox/hello.1.txt>
        self.queue.put(('created', e.src_path))

    def on_modified(self, e):
        # e -> <FileModifiedEvent: src_path=/Users/mikeboers/fi/dev/midx/sandbox/hello.1.txt>
        self.queue.put(('modified', e.src_path))

    def on_deleted(self, e):
        # e -> <FileDeletedEvent: src_path=/Users/mikeboers/fi/dev/midx/sandbox/hello.3.txt>
        pass

    def on_moved(self, e):
        # e -> <FileMovedEvent: src_path=/Users/mikeboers/fi/dev/midx/sandbox/hello.2.txt, dest_path=/Users/mikeboers/fi/dev/midx/sandbox/goodbyte.2.txt>
        pass


@command(
    argument('index'),
    argument('path', nargs='+'),
    help='watch paths for updates',
)
def watch(args):

    idx = Index(args.index)

    queue = Queue()
    observer = Observer()
    handler = EventHandler(queue)
    for path in args.path:
        observer.schedule(handler, path, recursive=True)
    observer.start()

    try:
        while True:
            type_, path = queue.get()
            if type_ in ('created', 'modified'):
                log.info('adding path: %s' % path)
                idx.add_path(path)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
