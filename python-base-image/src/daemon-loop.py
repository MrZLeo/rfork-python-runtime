import traceback
import json
import os
import time
from typing import NoReturn
import ol
import uuid
import socket
import array

import importlib.util
import sys
import base64


import tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.netutil
from flask import Flask

file_sock_path = 'cfork/f.sk'
file_sock = None

# global variables:
func = None
funcName = None

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello python!\n'


def start_faas_server(port: int, n: int) -> None:
    # time that start serverless function
    startTime = int(round(time.time() * 1000))
    logf = open("log.txt", "a")
    logf.write(str(n) + ": " + str(startTime) + "\n")
    logf.close()

    app.run(host='0.0.0.0',port=port)
    # global func
    # sys.path.append("/code")
    # # load code
    # if func is None:
    #     func = importlib.import_module('index')

    ####### hard code start ######
    # invoke the function
    # print("image_resize output: ")
    # f = open("/code/test.jpg", 'rb')
    # output = func.handler({'img': LoadTestImage(), 'height': 200, 'width': 200})
    # print(output)
    ####### hard code end #######
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.bind(("0.0.0.0", port))
    # sock.listen()
    # while True:
    #     client, _ = sock.accept()
    #     data = "hello python"
    #     client.sendall(bytes(data, "utf-8"))
    #     client.close()

    # while True:
    #     time.sleep(1)
        #print("I am not dead")


# def LoadTestImage():
#     f = open("/code/test.jpg", 'rb')
#     return str(base64.b64encode(f.read()), encoding='ascii')
#
# def Invoke():
#     return

# copied from https://docs.python.org/3/library/socket.html#socket.socket.recvmsg
def recv_fds(sock, msglen, maxfds):
    fds = array.array("i")   # Array of ints
    msg, ancdata, flags, addr = sock.recvmsg(msglen, socket.CMSG_LEN(maxfds * fds.itemsize))
    for cmsg_level, cmsg_type, cmsg_data in ancdata:
        if (cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS):
            # Append data, ignoring any truncated integers at the end.
            fds.frombytes(cmsg_data[:len(cmsg_data) - (len(cmsg_data) % fds.itemsize)])
    return msg, list(fds)


def start_fork_server():
    global file_sock
    global file_sock_path
    # print("daemon.py: start fork server on fd: %d" % file_sock.fileno())
    file_sock.setblocking(True)

    port = 8081
    log_no = 1

    while True:
        client, info = file_sock.accept()
        _, fds = recv_fds(client, 8, 2)
        pid = os.fork()
        target_fd = fds[0]
        pid_fd = fds[1]

        if pid:
            # the grand-parent process, catch next connection
            client.close()
            os.close(target_fd)
            os.close(pid_fd)
        else:
            # the parent process
            os.fchdir(target_fd)
            os.chroot(".")
            os.close(target_fd)

            errno = ol.setns(pid_fd)
            assert errno == 0
            os.close(pid_fd)

            pid = os.getpid()
            client.sendall(bytes(str(pid), 'utf8'))
            client.close()
            file_sock.close()
            file_sock = None

            # real function entry
            start_faas_server(port, log_no)
            exit()
        port += 1
        log_no += 1


def main():
    global file_sock
    file_sock = tornado.netutil.bind_unix_socket(file_sock_path)
    start_fork_server()

if __name__ == '__main__':
    main()
