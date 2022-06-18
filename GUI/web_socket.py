# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

# standard libaries
import queue
import select
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000


class IoTServer():
    def __init__(self):
        self.server = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET,
                               socket.SO_REUSEADDR,
                               1)
        self.server.setblocking(0)

        self.server.bind((HOST, PORT))
        self.server.listen(5)
        print(socket.gethostname())
        self.inputs = [self.server]
        self.outputs = []
        self.message_queue = {}

        # self.connections = []
        self.data = []
        self.run()

    def run(self):
        while self.inputs:
            print("websock loop")
            read_, write_, except_ = select.select(self.inputs,
                                                   self.outputs,
                                                   self.inputs)
            self.process_reads(read_)

    def process_reads(self, readables):
        for readable in readables:
            if readable is self.server:
                conn, addr = readable.accept()
                conn.setblocking(0)
                self.inputs.append(conn)
                self.message_queue[conn] = queue.Queue()
            else:
                data = readable.recv(1024)


if __name__ == "__main__":
    IoTServer()
