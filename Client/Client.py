import socket
from threading import Thread
import random
import os
import re
from time import sleep
import sys

BUFFER = 1024
SERVER_WELCOME_PORT = 5000
CLIENT_MESSAGE_PORT = 5002
FILE_TRANSFER_PORT = 5004
DELIMITER = "?CON?"
B_DELIMITER = b"?CON?"


class UnknownCommandException(Exception):
    pass


class Client():

    # Find and connect to the Namenode
    def __init__(self):
        # Find name server
        nameServerIP = self.findNameServer()
        # Establish connection
        nameServerMessengerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nameServerMessengerSocket.connect((nameServerIP, CLIENT_MESSAGE_PORT))

        self.soc = nameServerMessengerSocket
        self.curDir = "/"

    def findNameServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(b'Client try to find name server', ('<broadcast>', SERVER_WELCOME_PORT))
        data, addr = s.recvfrom(BUFFER)
        print(f'Name server found: {addr}')
        return addr[0]

    def init(self):
        self.soc.send("init".encode())

        print(f"Free space: {self.soc.recv(BUFFER).decode()}")
        # . Initialize the client storage on a new system,
        # should remove any existing file in the dfs root directory and return available size.

        # I also think it should ask for confirmation.

    # Create a new empty file at specified location(?)
    def create(self, filename):

        # TODO IMPLEMENT REALITVE LOCATION!!!!
        path = ""

        msg = DELIMITER.join(["create", filename, path])
        self.soc.send(msg.encode())

        # TODO receive data from servers

    def read(self):
        # TODO
        pass  # . Should allow to read any file from DFS (download a file from the DFS to the Client side).

    def _write(self, sock, filename, size):
        print("!!!Connected to server!!!")  # if it is not displayed ==> OOF

        # Counter initialization
        sas = 0
        pr_digit = '0'

        # Read/Send
        with open(filename, "rb") as f:
            for i in range(size):
                snd = f.read(BUFFER)
                if snd:

                    # To make output less annoying
                    msg = str(round(sas / float(size) * 100))
                    if pr_digit != msg[0] and round(sas / float(size) * 100) > 9:
                        print(msg, " %")
                        pr_digit = msg[0]

                    sas += BUFFER
                    sock.sendall(snd)
                else:
                    print("Transfer complete!!")
                    break

    def write(self, filename):
        """
        sas.py write sasamba.txt
        """
        # TODO IMPLEMENT REALITVE LOCATION!!!!
        size = os.path.getsize(filename)
        path = ""

        # Send metadata first
        msg = "write" + DELIMITER + filename + DELIMITER + str(size) + DELIMITER + path
        self.soc.send(msg.encode())

        # Wait for data about server
        response = self.soc.recv(BUFFER).decode()
        servers = response.split(DELIMITER)

        # Send to this server
        print(f"IPS are {servers}")
        sleep(1)
        for ip in servers:
            sock = socket.socket()
            sock.connect((ip, FILE_TRANSFER_PORT))
            self._write(sock, filename, size)
            print(f"Completed transfer to IP {ip}")

    # Delete given file from DFS
    def delete(self, filename):

        # TODO IMPLEMENT REALITVE LOCATION!!!!
        path = ""

        msg = DELIMITER.join(["del", filename, path])
        self.soc.send(msg.encode())

        # TODO get responses from server?

    # Get information about the file (any useful information - size, node id, etc.)
    def info(self, filename):

        # TODO IMPLEMENT REALITVE LOCATION!!!!
        path = ""

        msg = DELIMITER.join(["info", filename, path])
        self.soc.send(msg.encode())

        # TODO get responses from server

    # Copy file from src to dest
    def copy(self, src, dest):

        msg = DELIMITER.join(["copy", src, dest])
        self.soc.send(msg.encode())

        # TODO get responses from server?

    # Move file from src to dest
    def move(self, src, dest):

        msg = DELIMITER.join(["move", src, dest])
        self.soc.send(msg.encode())

        # TODO get responses from server?

    # Change GayErectory
    def open_dir(self, path):

        # What TODO with relative paths?

        msg = DELIMITER.join(["cd", path])
        self.soc.send(msg.encode())

        # TODO get responses from server?

    # Get list of files stored in the directory
    def read_dir(self, path):

        msg = DELIMITER.join(["ls", path])
        self.soc.send(msg.encode())

        # TODO get responses from server

    # Create a new directory
    def make_dir(self, dir_name):

        # TODO not sure about paths and what so ever

        msg = DELIMITER.join(["mkdir", dir_name])
        self.soc.send(msg.encode())

        # TODO get responses from server?

    def del_dir(self):
        pass
        # . Should allow to delete directory.
        # If the directory contains files the system should ask for confirmation from the user before deletion.

    def parseCommand(self, command):
        try:
            command = command.split()

            args = command[1:]
            command = command[0]
        except IndexError:
            args = []

        # TODO
        if command == "init":
            self.init()

        elif command == "create" or command == "make":
            self.create(args[0])

        elif command == "read" or command == "get":
            # TODO
            pass

        elif command == "write" or command == "put":
            self.write(args[0])

        elif command in ["delete", "del", "rm"]:
            self.delete(args[0])

        elif command == "info":
            self.info(args[0])

        elif command == "copy" or command == "cp":
            self.copy(args[0], args[1])

        elif command == "move" or command == "mv":
            self.move(args[0], args[1])

        elif command == "open" or command == "cd":
            self.open_dir(args[0])

        elif command == "read" or command == "ls":
            self.read_dir(args[0])

        elif command == "make_directory" or command == "mkdir":
            self.make_dir(args[0])

        elif command == "delete_directory" or command == "del_dir":
            pass

        else:
            raise UnknownCommandException


def print_help():
    # TODO
    print("List of available commands:\n")
    print(
        "init: Initialize the client storage on a new system; removes any existing file in the dfs root directory and returns available size.")
    print("create: Creates a new empty file.")
    print("read: Download a file from the DFS")
    print("write: Upload a file to the DFS")
    print("delete: Delete any file from DFS")
    print("info: Provide information about the file (size, node id, etc.)")
    print("copy: Create a copy of a file")
    print("move: Move a file to the specified path")
    print("open: Change directory")
    print("read: Return list of files, which are stored in the directory")
    print("mkdir: Create a new directory")
    print("del_dir: Delete directory. If the directory contains files, asks for confirmation before deletion")


def main():
    # Always print help at the start of the program.
    # In case user only querried help, do not execute anything else
    print_help()
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            return 0

    client = Client()

    while True:
        command = input()
        try:
            client.parseCommand(command)
        except UnknownCommandException:
            continue
        except IndexError:
            print("Provide more arguments")

        # nameServerMessengerSocket.send(b"Hello")
        # sleep(3)


if __name__ == '__main__':
    main()
