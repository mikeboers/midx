import os
from Queue import Queue

try:
    from . import fanotify as fan
except ImportError:
    fan = None
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler


if fan is None:

    class EventHandler(FileSystemEventHandler):

        def __init__(self, queue):
            super(EventHandler, self).__init__()
            self.queue = queue
        
        def on_created(self, e):
            self.queue.put(e.src_path)

        def on_modified(self, e):
            self.queue.put(e.src_path)

        def on_deleted(self, e):
            pass

        def on_moved(self, e):
            self.queue.put(e.dest_path)


def _iter_fanotify(roots):
    fd = fan.init()
    try:
        for path in roots:
            fan.mark(fd, path, True)
        while True:
            pid, mask, path = fan.read(fd)
            if any(os.path.commonprefix([path, root]) == root for root in roots):
                yield path
    finally:
        os.close(fd)


def _iter_watchdog(roots):
    queue = Queue()
    observer = Observer()
    handler = EventHandler(queue)
    for path in roots:
        observer.schedule(handler, path, recursive=True)
    observer.start()
    try:
        while True:
            yield queue.get()
    finally:
        observer.stop()


def iter_modified_files(roots):
    roots = [os.path.abspath(x) for x in roots]
    return _iter_fanotify(roots) if fan is not None else _iter_watchdog(roots)


