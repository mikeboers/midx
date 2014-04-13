#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/fanotify.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <Python.h>


#define BAIL_ON_ERROR(res) {if (check_error(res)) return NULL; }

static int check_error(res) {
    if (res >= 0) {
        return 0;
    }
    PyErr_SetFromErrno(PyExc_OSError);
    return 1;
}


static PyObject *
pyfanotify_init(PyObject *self, PyObject *args)
{
    int fd = fanotify_init(FAN_CLASS_NOTIF, O_RDONLY);
    BAIL_ON_ERROR(fd);

    return Py_BuildValue("i", fd);
}

static PyObject *
pyfanotify_mark(PyObject *self, PyObject *args)
{
    int fd, isdir;
    const char *path;

    if (!PyArg_ParseTuple(args, "isi", &fd, &path, &isdir)) return NULL;

    int res = fanotify_mark(
        fd,
        FAN_MARK_ADD | (isdir ? FAN_MARK_MOUNT : 0),
        FAN_MODIFY | FAN_CLOSE_WRITE | FAN_EVENT_ON_CHILD | FAN_ONDIR,
        AT_FDCWD,
        path
    );
    BAIL_ON_ERROR(res);

    Py_INCREF(Py_None);
    return Py_None;

}


static PyObject *
pyfanotify_read(PyObject *self, PyObject *args)
{
    int fd;
    ssize_t bytes_read, link_len;
    char fdpath[32];
    char path[PATH_MAX + 1];
    struct fanotify_event_metadata metadata;
    PyObject *res;

    if (!PyArg_ParseTuple(args, "i", &fd)) return NULL;

    bytes_read = read(fd, &metadata, sizeof(struct fanotify_event_metadata));
    if (bytes_read < sizeof(struct fanotify_event_metadata)) {
        PyErr_SetString(PyExc_RuntimeError, "incomplete read");
        return NULL;
    }
    if (metadata.mask & FAN_Q_OVERFLOW) {
        PyErr_SetString(PyExc_RuntimeError, "queue overflow");
        return NULL;
    }

    if (metadata.fd >= 0) {
        sprintf(fdpath, "/proc/self/fd/%d", metadata.fd);
        link_len = readlink(fdpath, path, sizeof(path) - 1);
        res = PyString_FromStringAndSize(path, link_len);
        close(metadata.fd);
    } else {
        res = Py_None;
        Py_INCREF(Py_None);
    }

    return res;
}

static PyMethodDef FanotifyMethods[] = {
    {"init",  pyfanotify_init, METH_VARARGS, "xxx"},
    {"mark",  pyfanotify_mark, METH_VARARGS, "xxx"},
    {"read",  pyfanotify_read, METH_VARARGS, "xxx"},
    {NULL, NULL, 0, NULL}
};


PyMODINIT_FUNC
initfanotify(void)
{
    PyObject *m = Py_InitModule("midx.notify.fanotify", FanotifyMethods);
    if (!m) return;
}
