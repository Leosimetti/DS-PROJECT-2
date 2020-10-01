import sys
import socket
from threading import Thread
import os
from time import sleep

PORT = 1488
# Stores files

# Gives access to files

# Some interaction with naming server

# Send message to NameServer on INIT, maybe even broadcast it

BUFF = 1488  # Unified constant


class Heart(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        print("Heart started beating")

    def run(self):
        while True:
            self.sock.send("ALIVE".encode())
            print("ALIVE!!!!!!!!")
            sleep(1.5)


# Thread to listen one particular client
# class ClientListener(Thread):
#     def __init__(self, name: str, sock: socket.socket):
#         super().__init__(daemon=True)
#         self.sock = sock
#         self.name = name
#
#     # clean up
#     def _close(self):
#         clients.remove(self.sock)
#         self.sock.close()
#         print(self.name + ' disconnected')
#
#     def run(self):
#
#         # Unpack the metadata that goes as the first package
#         received = self.sock.recv(BUFF).decode()
#         filename, filesize = received.split("?CON?")
#
#         print(f"[{self.name}] Starting transfer of {filename}")
#
#         # Make the data actually useful
#         filename = os.path.basename(filename)
#         filesize = int(filesize)
#
#         # Counter initialization
#         sas = 0.0
#
#         # Receive/Write
#
#         with open(filename, "wb") as f:
#
#             for i in range(filesize):
#                 # Will return zero when done
#                 rcv = self.sock.recv(BUFF)
#                 if rcv:
#                     # Write received data
#                     sas += BUFF
#                     f.write(rcv)
#                 else:
#                     print(f"[{self.name}] Transfer complete!!")
#                     break
#         self._close()

def find_batya():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(b'Dai IP', ('<broadcast>', 1337))
    batya = s.recv(1024)
    print(batya)
    return batya

def main():
    BATYA_IP = find_batya()

    #BATYA_IP = input("ENTER BATYA IP:")  # sys.argv[2]
    print("FINDING BATYA...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((BATYA_IP, int(PORT)))
    print("!!!Connected to BATYA!!!")
    Heart(s).start()


if __name__ == "__main__":
    main()
    while True:
        pass
