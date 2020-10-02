# Only one unique server; single one

# It is proxy server more or less

# Naming servers also provide a way for storage servers to register their presence.

# Each file should be replicated on at least 2 Storage Servers.
# If one of the Storage Server goes down, files, that is stored should be replicated to another Storage Server.

# Choose the serv with the least load?? Via heartbeat msgs containing Free space and # of requests

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

filesDict = {}
storageServersFiles = {}

REPLICAS = 1


class FileInfo:
    def __init__(self, fileName: str, fileSize: int, filePath: str):
        self.serverContainers = set()
        self.fileSize = fileName
        self.fileName = fileSize
        self.filePath = filePath

    def addContainer(self, serverIP):
        self.serverContainers.add(serverIP)

    def addContainers(self, serverIPs):
        self.serverContainers.update(serverIPs)

    def deleteContainer(self, serverIP):
        self.serverContainers.remove(serverIP)

    def correspondsTo(self, otherFileInfo):
        if self.filePath == otherFileInfo.filePath and self.fileName == otherFileInfo.fileName:
            return True

    def __str__(self):
        return f"FileName: {self.fileName}, FileSize: {self.fileSize}, FilePath: {self.filePath}"


def receive_file(fileInfo: FileInfo, file, clientInfo):
    servers = random.sample(SONS, REPLICAS)
    fileInfo.addContainers(servers)
    filesDict[fileInfo.fileName] = fileInfo
    for server in servers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((server, CMND_PORT))
        storageServersFiles[server] = fileInfo
        sock.send(b'receive?CON?')
        sock.send(file)


def create_file(fileName: str, filePath: str):
    servers = random.sample(SONS, REPLICAS)
    newFile = FileInfo(fileName, 0, filePath)
    newFile.addContainers(servers)
    filesDict[newFile.fileName] = newFile
    for server in servers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((server, CMND_PORT))
        print(f"Creation of {newFile}")
        storageServersFiles[server] = newFile
        sock.send(b'create?CON?')


def send_file(fileInfo: FileInfo, clientInfo):
    servers = filesDict[fileInfo.fileName].serverContainers
    server = random.sample(servers)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((server, CMND_PORT))
    sock.send(b'send?CON?')


def get_fileInfo(fileInfo: FileInfo):
    pass


# How to translate replicas?
def copy_file(fileInfo: FileInfo, newFileInfo: FileInfo):
    servers = filesDict[fileInfo.fileName].serverContainers
    newFileInfo.addContainers(servers)
    for server in servers:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((server, CMND_PORT))
        storageServersFiles[server] = newFileInfo
        sock.send(b'copy?CON?')


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

            create_file("NUDES", "aaa")
            # create_file("NUDES")
            # create_file("NUDES")
            # create_file("SA")
            # create_file("vdav")
            # create_file("asv")
            # create_file("NUDES")
            # create_file("AS")
            # create_file("NUDES")


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
