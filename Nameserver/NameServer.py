# Only one unique server; single one

# It is proxy server more or less

# Naming servers also provide a way for storage servers to register their presence.

# Each file should be replicated on at least 2 Storage Servers.
# If one of the Storage Server goes down, files, that is stored should be replicated to another Storage Server.

# Choose the serv with the least load

import socket
from threading import Thread
import random
import os
import re
from time import sleep

SONS = []
BUFF = 72  # Unified constant
PORT = 1488
CLIENT_PORT = 6969
CMND_PORT = 2280
fileMap = {}
storageServersFiles = {}


class StorageServerDemon:
    def recieve_file(self, fileinfo, file):
        servers = random.sample(SONS, 3)
        for server in servers:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server['raddr'][0], CMND_PORT))
            fileMap[fileinfo] = server
            storageServersFiles[server] = fileinfo
            sock.send(b'receive?CON?'+fileinfo.encode())
            sock.send(file)



# Thread to listen one particular client
class HeartListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        SONS.remove(self.sock)
        self.sock.close()
        print(self.name + ' ded')

    def run(self):
        try:
            while self.sock.recv(BUFF):
                print(f' {self.name} IS ALIVE!!!!!!! ')
                sleep(2)
        except ConnectionResetError:
            print("BLYA, SON ZDOX")
            self._close()


class WelcomeSocket(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            print(f"{data} : {addr}")
            self.sock.sendto(b'Dayu IP', addr)


class Backend(Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        next_name = 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))
        sock.listen()
        print("Waiting for SONS...")
        while True:
            con, addr = sock.accept()
            SONS.append(con)
            name = 'SON ' + str(next_name)
            next_name += 1
            print(f"{name} " + str(addr) + ' WAS FOUND!!!')
            # start new thread to deal with client
            HeartListener(name, con).start()


def main():
    welcome_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    welcome_sock.bind(("", 1337))
    WelcomeSocket(welcome_sock).start()

    Backend().start()

    next_name = 1
    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and immediately start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', CLIENT_PORT))
    sock.listen()
    print("Waiting for Clients...")
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        name = 'Client ' + str(next_name)
        next_name += 1
        print(f"{name} " + str(addr) + ' WAS FOUND!!!')
        # start new thread to deal with client

    while True:
        pass


if __name__ == "__main__":
    main()
