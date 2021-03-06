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
SIBLING_PORT = 5005
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


def correctPath(name):
    return name.replace("/", '∫%&FOLD&%∫')


class ServerMessenger(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__()
        print("Messaging connection established")
        self.sock = sock

    def init(self):
        shutil.rmtree(os.getcwd() + "/DFS")
        os.mkdir("DFS")

        free_space = shutil.disk_usage(os.getcwd())[2]
        self.sock.send("FREE".encode() + B_DELIMITER + str(free_space).encode())
        print(f"Available space: {free_space // 1024 // 1024 // 8} Mb")

    def read(self, metadata):
        print(f"send {metadata}")
        filename = metadata[2] + metadata[0]
        filename = correctPath(filename)
        filename = "./DFS/" + os.path.basename(filename)
        filesize = int(metadata[1])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', FILE_TRANSFER_PORT))
        sock.listen()

        con, addr = sock.accept()

        sas = 0
        pr_digit = '0'
        # Read/Send
        with open(filename, "rb") as f:
            for i in range(filesize):
                snd = f.read(BUFFER)
                if snd:

                    # To make output less annoying
                    msg = str(round(sas / float(filesize) * 100))
                    if pr_digit != msg[0] and round(sas / float(filesize) * 100) > 9:
                        print(msg, " %")
                        pr_digit = msg[0]

                    sas += BUFFER
                    con.sendall(snd)
                else:
                    print("Transfer complete!!")
                    break

        sock.close()
        pass

    def write(self, metadata, PORT):
        print(f"rcv {metadata}")
        filename = metadata[2] + metadata[0]
        filename = correctPath(filename)
        filename = "./DFS/" + os.path.basename(filename)
        filesize = int(metadata[1])

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', PORT))
        sock.listen()

        con, addr = sock.accept()

        # Receive/Write

        print("Starting transfer")
        with open(filename, "wb") as f:

            for i in range(filesize):
                # Will return zero when done
                rcv = con.recv(BUFFER)
                if rcv:
                    f.write(rcv)
                else:
                    print(f"Transfer of {metadata} complete!!")
                    break
            con.close()
        sock.close()

    @staticmethod
    def create(metadata):
        filename = metadata[2] + metadata[0]
        filename = correctPath(filename)
        print(f"create {filename}")
        filename = "./DFS/" + os.path.basename(filename)
        with open(filename, "wb") as f:
            pass

    @staticmethod
    def delete(metadata):
        print(f"del {metadata}")
        filename = metadata[2] + metadata[0]
        filename = correctPath(filename)
        filename = "./DFS/" + os.path.basename(filename)
        os.remove(filename)

    @staticmethod
    def deldir(metadata):
        sacrifice_mark = correctPath(metadata[0])
        for file in os.listdir("./DFS"):
            if file.startswith(sacrifice_mark):
                print(f"Removing file {file}")
                try:
                    os.remove("./DFS/" + file)
                except:
                    print(f"Unlucky; no {file}")
                    pass

    @staticmethod
    def copy(metaData):
        filename = metaData[2] + metaData[0]
        filename = correctPath(filename)
        filename = "./DFS/" + os.path.basename(filename)
        print(filename)
        newName = metaData[5] + metaData[3]
        newName = correctPath(newName)
        newName = "./DFS/" + os.path.basename(newName)
        print(newName)
        print(os.path.basename(filename))

        if os.path.exists(filename):
            original_name = filename
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

    @staticmethod
    def sendSibling(metaData):
        print(f" Sharing {metaData[1:]} with {metaData[0]}")

        server = metaData[0]
        filename = metaData[3] + metaData[1]
        filename = correctPath(filename)
        size = int(metaData[2])

        sock = socket.socket()
        sleep(0.1588)
        sock.connect((server, SIBLING_PORT))

        with open(filename, "wb") as f:
            for i in range(size):
                rcv = sock.recv(BUFFER)
                if rcv:
                    f.write(rcv)
                else:
                    print("File download complete!!")
                    break

    def run(self):
        while True:
            received = self.sock.recv(BUFFER)
            if received != b'':
                data = received.decode().split(DELIMITER)
                requestType, metaData = data[0], data[1:]
                if requestType == "copy":
                    self.copy(metaData)
                elif requestType == "write":
                    self.write(metaData, FILE_TRANSFER_PORT)
                elif requestType == "read":
                    self.read(metaData)
                elif requestType == "create":
                    self.create(metaData)
                elif requestType == "init":
                    self.init()
                elif requestType == "deldir":
                    self.deldir(metaData)
                elif requestType == "del":
                    self.delete(metaData)
                elif requestType == "serverSend":
                    self.sendSibling(metaData)
                elif requestType == "serverReceive":
                    self.write(metaData[1:], SIBLING_PORT)

                elif requestType == "":
                    pass
                elif requestType == "":
                    pass
                elif requestType == "":
                    pass
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
    try:
        os.mkdir("DFS")
    except:
        pass

    try:
        shutil.rmtree(os.getcwd() + "/DFS")
        os.mkdir("DFS")
    except:
        pass

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
