#include <Python.h>
#include <arpa/inet.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <sys/wait.h>

static PyObject *ol_setns(PyObject *module, PyObject *args)
{
    int fd, res;

    if (!PyArg_ParseTuple(args, "i", &fd))
        return Py_BuildValue("i", -1);

    res = setns(fd, CLONE_NEWIPC | CLONE_NEWNS | CLONE_NEWUTS);
    return Py_BuildValue("i", res);
}

static PyMethodDef OlMethods[] = {
    { "setns", (PyCFunction)ol_setns, METH_VARARGS, "setns" },
    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef olMod = { PyModuleDef_HEAD_INIT, "ol", NULL, -1, OlMethods };

PyMODINIT_FUNC PyInit_ol(void) { return PyModule_Create(&olMod); }
