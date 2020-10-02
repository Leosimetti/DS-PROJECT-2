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
REPLICAS = 3


class StorageServerDemon:
    def recieve_file(self, fileInfo, file, clientInfo):
        servers = random.sample(SONS, REPLICAS)
        for server in servers:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server, CMND_PORT))
            if fileInfo in fileMap:
                fileMap[fileInfo].append(server)
            else:
                fileMap[fileInfo] = [server]
            storageServersFiles[server] = fileInfo
            sock.send(b'receive?CON?' + fileInfo.encode() + b'?CON?' + clientInfo.encode())
            sock.send(file)

    def create_file(self, fileInfo):
        servers = random.sample(SONS, REPLICAS)
        for server in servers:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server, CMND_PORT))
            if fileInfo in fileMap:
                fileMap[fileInfo].append(server)
            else:
                fileMap[fileInfo] = [server]
            storageServersFiles[server] = fileInfo
            sock.send(b'create?CON?' + fileInfo.encode())

    def send_file(self, fileInfo, clientInfo):
        servers = fileMap[fileInfo]
        server = random.sample(servers)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((server, CMND_PORT))
        sock.send(b'send?CON?' + fileInfo.encode() + b'?CON?' + clientInfo.encode())

    def get_fileInfo(self, fileInfo):
        pass

    # How to translate replicas?
    def copy_file(self, fileInfo, newFileInfo):
        servers = fileMap[fileInfo]
        for server in servers:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((server, CMND_PORT))
            if newFileInfo in fileMap:
                fileMap[newFileInfo].append(server)
            else:
                fileMap[newFileInfo] = [server]
            storageServersFiles[server] = newFileInfo
            sock.send(b'copy?CON?' + fileInfo.encode())



# Thread to listen one particular client
class HeartListener(Thread):
    def __init__(self, name: str, sock: socket.socket, ip):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        self.ip = ip

    # clean up
    def _close(self):
        SONS.remove(self.ip)
        self.sock.close()
        print(self.name + ' ded')

    def run(self):
        try:
            while self.sock.recv(BUFF):
                # print(f' {self.name} IS ALIVE!!!!!!! ')
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
            SONS.append(addr[0])
            name = 'SON ' + str(next_name)
            next_name += 1
            print(f"{name} " + str(addr) + ' WAS FOUND!!!')
            # start new thread to deal with client
            HeartListener(name, con, addr[0]).start()


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
