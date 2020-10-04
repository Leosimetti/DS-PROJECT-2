import socket
from threading import Thread
import os
from time import sleep
import shutil

BUFFER = 1024
SERVER_WELCOME_PORT = 5000
SERVER_HEARTBEAT_PORT = 5001
CLIENT_MESSAGE_PORT = 5002
SERVER_MESSAGE_PORT = 5003
FILE_TRANSFER_PORT = 5004
DELIMITER = "?CON?"
B_DELIMITER = b"?CON?"


class Heart(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__()
        print("Heartbeat is initiated")
        self.sock = sock

    def run(self):
        while True:
            self.sock.send("ALIVE".encode())
            sleep(3)


class ServerMessenger(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__()
        print("Messaging connection established")
        self.sock = sock


    def init(self):
        # TODO IT IS NOTE SUPPOSED TO BE LIKE THIS!!!!!!!!!!!
        # TODO AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        shutil.rmtree(os.getcwd() + "/DFS")
        os.mkdir("DFS")

        free_space = shutil.disk_usage(os.getcwd())[2]
        self.sock.send("FREE".encode() + B_DELIMITER + str(free_space).encode())
        print(f"Available space: {free_space}")

    def write(self, metadata):
        print(f"rcv {metadata}")
        filename = metadata[2] + metadata[0]  # TODO may cause bugs
        filename = "./DFS/" + os.path.basename(filename)
        filesize = int(metadata[1])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', FILE_TRANSFER_PORT))
        sock.listen()

        con, addr = sock.accept()

        # Counter initialization
        sas = 0.0

        # Receive/Write

        print("Starting transfer")
        with open(filename, "wb") as f:

            for i in range(filesize):
                # Will return zero when done
                rcv = con.recv(BUFFER)
                if rcv:
                    # Write received data
                    sas += BUFFER
                    f.write(rcv)
                else:
                    print(f"Transfer of {metadata} complete!!")
                    break

    @staticmethod
    def create(metaData):
        filename = metaData[0]
        print(f"create {filename}")
        filename = os.path.basename(filename)
        with open(filename, "wb") as f:
            pass

    @staticmethod
    def deldir(metadata):
        pass

    @staticmethod
    def copy(metaData):
        filename = metaData[0]
        newName = metaData[3]

        if os.path.exists(os.path.basename(filename)):
            original_name = os.path.basename(filename)
            # add 'copy' part
            while os.path.isfile(newName):
                try:
                    name, ext = newName.split(".")
                except:
                    name = newName
                    ext = ""
                if "_copy_" in name:
                    init_name, copy_ind = name.split("_copy_")
                    copy_ind = int(copy_ind) + 1
                    name = init_name + "_copy_" + str(copy_ind)
                else:
                    name = name + "_copy_1"
                newName = name + "." + ext
            shutil.copy2(original_name, newName)
        else:
            print("No such file exists")

    def run(self):
        while True:
            received = self.sock.recv(BUFFER)
            if received != b'':
                data = received.decode().split(DELIMITER)
                requestType, metaData = data[0], data[1:]
                if requestType == "copy":
                    self.copy(metaData)
                elif requestType == "write":
                    self.write(metaData)
                elif requestType == "read":
                    print("TOLYA ZAIMPLMENTb")
                    print(f"send {metaData}")
                elif requestType == "create":
                    self.create(metaData)
                elif requestType == "init":
                    self.init()
                elif requestType == "deldir":
                    self.deldir()
                else:
                    print(f"Unknown request: {requestType}")
            else:
                sleep(1)


def findNameServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(b'Storage server try to find name server', ('<broadcast>', SERVER_WELCOME_PORT))
    data, addr = s.recvfrom(1024)
    print(f'Name server found: {addr}')
    return addr[0]


def main():

    os.mkdir("DFS")

    # Find name server
    NameServerIP = findNameServer()
    # Start heartbeat
    heartSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    heartSocket.connect((NameServerIP, SERVER_HEARTBEAT_PORT))
    Heart(heartSocket).start()
    # NameServer messaging socket
    sleep(1)  # Let name server initialize heartbeat and save information about server
    serverMessagingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverMessagingSocket.connect((NameServerIP, SERVER_MESSAGE_PORT))
    ServerMessenger(serverMessagingSocket).start()

    while True:
        pass


if __name__ == '__main__':
    main()
