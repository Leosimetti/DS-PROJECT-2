import socket
from threading import Thread
import random
import os
import re
from time import sleep

BUFFER = 1024
SERVER_WELCOME_PORT = 5000
CLIENT_MESSAGE_PORT = 5002
DELIMITER = "?CON?"
B_DELIMITER = b"?CON?"


class Client():

    # Find and connect to the Namenode
    def __init__(self):
        # Find name server
        NameServerIP = findNameServer()
        # Establish connection
        nameServerMessengerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nameServerMessengerSocket.connect((NameServerIP, CLIENT_MESSAGE_PORT))

        self.soc = nameServerMessengerSocket
    

    def findNameServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(b'Client try to find name server', ('<broadcast>', SERVER_WELCOME_PORT))
        data, addr = s.recvfrom(1024)
        print(f'Name server found: {addr}')
        return addr[0]


    def init(self):
        pass
        # . Initialize the client storage on a new system,
        # should remove any existing file in the dfs root directory and return available size.


    def create(self, filename):
        pass  # . Should allow to create a new empty file.


    def read(self):
        pass  # . Should allow to read any file from DFS (download a file from the DFS to the Client side).


    def write(self, filename):
        """
        sas.py write sasamba.txt
        """
        # TODO IMPLEMENT REALITVE LOCATION!!!!
        size = os.path.getsize(filename)
        path = ""

        # Send metadata first
        msg = "receive" + DELIMITER + filename + DELIMITER + str(size)+ DELIMITER + path
        self.soc.send(msg.encode())

        # Wait for data about server
        rcv1 = self.soc.recv(BUFFER).decode()
        rcv2 = self.soc.recv(BUFFER).decode()

        # Send to this server
        print(f"IPS are {rcv1} and {rcv2}")


    def delete(self):
        pass  # . Should allow to delete any file from DFS


    def info(self):
        pass  # . Should provide information about the file (any useful information - size, node id, etc.)


    # Copy file from src to dest
    def copy(self):
        pass  # . Should allow to create a copy of file.


    # Move file from src to dest
    def move(self, src, dest):
        pass  # ". Should allow to move a file to the specified path.


    # Change GayErectory
    def open_dir(self):
        pass  # . Should allow to change directory


    # ls
    def read_dir(self):
        pass  # . Should return list of files, which are stored in the directory.


    def make_dir(self):
        pass  # . Should allow to create a new directory.


    def del_dir(self):
        pass
        # . Should allow to delete directory.
        # If the directory contains files the system should ask for confirmation from the user before deletion.


    def parseCommand(self, command):
        command = command.split()

        args = command[1:]
        command = command[0]

        # TODO
        if command == "init":
            init()
        elif command == "create" or command == "make":
            create(args[0])
        elif command == "read" or command == "get":
            pass
        elif command == "write" or command == "put":
            pass
        elif command in ["delete", "del", "rm"]:
            pass
        elif command == "info":
            pass
        elif command == "copy" or command == "cp":
            pass
        elif command == "move" or command == "mv":
            pass
        elif command == "open" or command == "cd":
            pass
        elif command == "read" or command == "ls":
            pass
        elif command == "make_directory" or command == "mkdir":
            pass
        elif command == "delete_directory" or command == "del_dir":
            pass
        else:
            raise UnknownCommandException


def main():
    client = Client()

    while True:
        command = input()
        try:
            client.parseCommand(command)
        except UnknownCommandException:
            pass
        

        # nameServerMessengerSocket.send(b"Hello")
        # sleep(3)


if __name__ == '__main__':
    main()
