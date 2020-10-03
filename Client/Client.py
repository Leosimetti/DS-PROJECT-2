import socket
from threading import Thread
import random
import os
import re
from time import sleep

BUFFER = 1024
SERVER_WELCOME_PORT = 5000
CLIENT_MESSAGE_PORT = 5002


def findNameServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(b'Client try to find name server', ('<broadcast>', SERVER_WELCOME_PORT))
    data, addr = s.recvfrom(1024)
    print(f'Name server found: {addr}')
    return addr[0]


def init():
    pass
    # . Initialize the client storage on a new system,
    # should remove any existing file in the dfs root directory and return available size.


def create():
    pass  # . Should allow to create a new empty file.


def read():
    pass  # . Should allow to read any file from DFS (download a file from the DFS to the Client side).


def write(soc, filename):
    """
    sas.py write sasamba.txt
    """
    # TODO IMPLEMENT REALITVE LOCATION!!!!
    size = os.path.getsize(filename)
    path = ""

    # Send metadata first
    msg = "receive" + "?CON?" + filename + "?CON?" + str(size)+"?CON?" + path
    soc.send(msg.encode())

    # Wait for data about server
    rcv1 = soc.recv(BUFFER).decode()
    rcv2 = soc.recv(BUFFER).decode()

    # Send to this server
    print(f"IPS are {rcv1} and {rcv2}")


def delete():
    pass  # . Should allow to delete any file from DFS


def info():
    pass  # . Should provide information about the file (any useful information - size, node id, etc.)


def copy():
    pass  # . Should allow to create a copy of file.


def move():
    pass  # ". Should allow to move a file to the specified path.


def open_dir():
    pass  # . Should allow to change directory


def read_dir():
    pass  # . Should return list of files, which are stored in the directory.


def make_dir():
    pass  # . Should allow to create a new directory.


def del_dir():
    pass
    # . Should allow to delete directory.
    # If the directory contains files the system should ask for confirmation from the user before deletion.


def main():
    # Find name server
    NameServerIP = findNameServer()
    # Establish connection
    nameServerMessengerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    nameServerMessengerSocket.connect((NameServerIP, CLIENT_MESSAGE_PORT))
    while True:
        # TODO change on CLI INPUT
        nameServerMessengerSocket.send(b"Hello")
        sleep(3)


if __name__ == '__main__':
    main()
