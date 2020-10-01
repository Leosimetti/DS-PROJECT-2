import sys
import socket
from threading import Thread
import os

PORT = 1488
# Stores files

# Gives access to files

# Some interaction with naming server

# Send message to NameServer on INIT, maybe even broadcast it

BUFF = 1488 # Unified constant


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):

        # Unpack the metadata that goes as the first package
        received = self.sock.recv(BUFF).decode()
        filename, filesize = received.split("?CON?")

        print(f"[{self.name}] Starting transfer of {filename}")

        # Make the data actually useful
        filename = os.path.basename(filename)
        filesize = int(filesize)

        # Counter initialization
        sas = 0.0

        # Receive/Write

        with open(filename, "wb") as f:

            for i in range(filesize):
                # Will return zero when done
                rcv = self.sock.recv(BUFF)
                if rcv:
                    # Write received data
                    sas += BUFF
                    f.write(rcv)
                else:
                    print(f"[{self.name}] Transfer complete!!")
                    break
        self._close()


def main():
    next_name = 1

    # COntact batya
    BATYA_IP = sys.argv[2]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((BATYA_IP, PORT))
    sock.listen()
    print("Waiting for clients...")
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(f"[{name}] " + str(addr) + ' connected')
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()



