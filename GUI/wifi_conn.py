# Copyright (c) 2019 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitatus Lopin"

import queue
import select, socket, sys
import threading


HOST = socket.gethostbyname(socket.gethostname())
print(f"Host: {HOST}")
PORT = 10540


class WifiHub(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running_flag = True

        self.write_queue = queue.Queue()
        self.write_event = threading.Event()
        self.read_queue = queue.Queue()
        self.read_event = threading.Event()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(0)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.inputs = [self.server]
        self.outputs = []
        self.start()

    def write(self):
        while self.running_flag:
            self.write_event.wait()
            self.write_event.clear()
            if self.write_queue.qsize() > 0:
                pass

    def run(self):
        while True:
            print("hello")
            readable, writable, exceptional = select.select(
                self.inputs, self.outputs, self.inputs)
            for s in readable:
                if s is self.server:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.message_queues[connection] = queue.Queue()
                else:
                    data = s.recv(1024)
                    if data:
                        self.message_queues[s].put(data)
                        if s not in self.outputs:
                            self.outputs.append(s)
                    else:
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()
                        del message_queues[s]



if __name__ == "__main__":
    WifiHub()
