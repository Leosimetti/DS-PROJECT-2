# TOLYA, SDELAY CLI TYT


import os
import socket
import sys
from time import sleep

BUFF = 1488
PORT = 6969


def find_batya():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(b'Dai IP', ('<broadcast>', 1337))
    data, addr = s.recvfrom(1024)
    print(f'Server found at {addr}')
    return addr


def init():
    pass  # . Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return available size.


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
    msg = "receive" + "?CON?" + filename + "?CON?" + str(size)+"?CON?"+ path
    soc.send(msg.encode())

    # Wait for data about server
    rcv1 = soc.recv(BUFF).decode()
    rcv2 = soc.recv(BUFF).decode()

    # Send to this server
    print(f"IPS are {rcv1} and {rcv2}")

    # Read/Send loop
    # sas = 0
    # with open(filename, "rb") as f:
    #     for i in range(size):
    #         snd = f.read(BUFF)
    #         if snd:
    #
    #             sas += BUFF
    #             soc.sendall(snd)
    #         else:
    #             print("Transfer complete!!")
    #             break


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
    pass  # . Should allow to delete directory.  If the directory contains files the system should ask for confirmation from the user before deletion.


def main():
    print("FINDING SERVER...")
    BATYA_IP = find_batya()[0]  # input("ENTER BATYA IP:")
    soc = socket.socket()  # socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((BATYA_IP, int(PORT)))
    print("Connected to Nameserver...")

    try:
        cmd = sys.argv[1]

        if cmd == "write":
            write(soc, sys.argv[2])
    except:
        pass
    # Cleanup
    soc.close()


if __name__ == "__main__":
    main()

    while True:
        print("RODILSYA")
        sleep(10)
        print("ZHIVU PERZHU")
        sleep(60)
        print("ZHIVU DOZHIVAYU")
        sleep(60)
        print("STAL DEDOM")
        sleep(10)
        print("TENSEI !!!!")
