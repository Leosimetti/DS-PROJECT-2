# Only one unique server; single one

# It is proxy server more or less

# Naming servers also provide a way for storage servers to register their presence.

# Each file should be replicated on at least 2 Storage Servers. If one of the Storage Server goes down, files, that is stored should be replicated to another Storage Server.

# Choose the serv with the least load

import socket
from threading import Thread
import os
import re
from time import sleep


SONS = []
BUFF = 72 # Unified constant
PORT = 1488

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

        # Unpack the metadata that goes as the first package
        # received = self.sock.recv(BUFF).decode()
        # filename, filesize = received.split("?CON?")
        #
        # print(f"[{self.name}] Starting transfer of {filename}")
        #
        # # Make the data actually useful
        # filename = os.path.basename(filename)
        # filesize = int(filesize)
        #
        # # Counter initialization
        # sas = 0.0

        # Receive/Write

        try:
            while self.sock.recv(BUFF):
                print(f' {self.name} IS ALIVE!!!!!!! ')
                sleep(2)
        except ConnectionResetError:
            print("BLYA, SON ZDOX")

        # with open(filename, "wb") as f:
        #
        #     for i in range(filesize):
        #         # Will return zero when done
        #         rcv = self.sock.recv(BUFF)
        #         if rcv:
        #             # Write received data
        #             sas += BUFF
        #             f.write(rcv)
        #         else:
        #             print(f"[{self.name}] Transfer complete!!")
        #             break
        self._close()


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', PORT))
    sock.listen()
    print("Waiting for SONS...")
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        SONS.append(con)
        name = 'SON ' + str(next_name)
        next_name += 1
        print(f"{name} " + str(addr) + ' WAS FOUND!!!')
        # start new thread to deal with client
        HeartListener(name, con).start()


if __name__ == "__main__":
    main()



