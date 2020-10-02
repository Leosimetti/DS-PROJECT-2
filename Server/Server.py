import sys
import socket
from threading import Thread
import os
from time import sleep

PORT = 1488
CMND_PORT = 2280
# Stores files

# Gives access to files

# Some interaction with naming server --> ✔ DONE

# Send message to NameServer on INIT, maybe even broadcast it --> ✔ DONE

BUFF = 1488  # Unified constant


class Heart(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        print("Heart started beating")

    def run(self):
        while True:
            self.sock.send("ALIVE".encode())
            # print("ALIVE!!!!!!!!")
            sleep(1.5)


class ProcessRequest(Thread):
    def __init__(self, sock: socket.socket, name: str):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name
        print(f"Started processing request {self.name}")

    def run(self):
        received = self.sock.recv(BUFF).decode()
        cmd_type, meta_data = received.split("?CON?")

        if cmd_type == "copy":
            print(f"cpy {meta_data}")
        elif cmd_type == "receive":
            print(f"rcv {meta_data}")
        elif cmd_type == "send":
            print(f"send {meta_data}")
        elif cmd_type == "create":
            print(f"create {meta_data}")
        else:
            print(" CHORT, TI SHTO ZAPRASHIVAESH, AAAAAAAAAA?")


def find_batya():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(b'Dai IP', ('<broadcast>', 1337))
    data, addr = s.recvfrom(1024)
    print(f'Batya found: {addr}')
    return addr


def store_file():
    pass


def give_file():
    pass


def main():
    BATYA_ADDR = find_batya()

    # BATYA_IP = input("ENTER BATYA IP:")  # sys.argv[2]
    print("FINDING BATYA...")
    h = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    h.connect((BATYA_ADDR[0], int(PORT)))
    print("!!!🍆🍆🍆🍆🍆🍆🍆 Connected to BATYA 🍆🍆🍆🍆🍆🍆🍆!!!")
    Heart(h).start()

    # For the clients
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', CMND_PORT))
    sock.listen()
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((BATYA_ADDR[0], int(PORT)))

    requests = []
    next_name = 1
    print("Waiting for Requests from BATYA...")
    while True:
        # blocking call, waiting for new request to arrive
        con, addr = sock.accept()
        requests.append(con)
        name = 'Req ' + str(next_name)
        next_name += 1
        print(f"{name} " + str(addr) + ' was accepted!!!')

        ProcessRequest(con, name).start()

        # start new thread to deal with client


if __name__ == "__main__":
    main()
