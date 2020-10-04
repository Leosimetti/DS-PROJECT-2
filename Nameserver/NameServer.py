import socket
from threading import Thread
import random
from time import sleep

BUFFER = 1024
SERVER_WELCOME_PORT = 5000
SERVER_HEARTBEAT_PORT = 5001
CLIENT_MESSAGE_PORT = 5002
SERVER_MESSAGE_PORT = 5003
DELIMITER = "?CON?"
B_DELIMITER = b"?CON?"
# TODO CHECK 2
REPLICAS = 1


class NameServer:
    def __init__(self):
        self.StorageServers = {}


# Dict {ServerIP:ServerName}
StorageServers = {}
# Dict {ServerIP:ServerMessageSocket}
StorageServerMessageSockets = {}

ClientIPs = []


class FilesTree:
    def __init__(self):
        a = FolderNode("root")


# Folder
class FolderNode:
    def __init__(self, name: str):
        self.name = name
        self.files = []
        self.folders = []

    def addFolder(self, node):
        self.folders.append(node)

    def removeFolder(self, node):
        self.folders.remove(node)

    def getFolder(self, folderName):
        for folder in self.folders:
            if folder.name == folderName:
                return folder
        return Exception

    def addFile(self, leaf):
        self.files.append(leaf)

    def removeFile(self, leaf):
        self.files.remove(leaf)

    def __str__(self):
        """
        String with all info about folders and files.
        """
        if len(self.folders) != 0:
            result = "Folders: \n\t"
            for folder in self.folders:
                result += f"{folder.name} "
            result += "\n"
        else:
            result = ""
        if len(self.files) != 0:
            result += "Files: \n\t"
            for fileInfo in self.files:
                result += f"{fileInfo.fileName} "
        else:
            result += "Directory does not contain any file"
        return result


class FileInfo:
    def __init__(self, fileName: str, filePath: str, fileSize: int):
        self.fileName = fileName
        self.filePath = filePath
        self.fileSize = fileSize
        self.storageServers = set()

    def fileLocation(self):
        """
        Return tuple of fileName and filePath
        """
        return self.fileName, self.filePath

    def addContainer(self, serverIP):
        self.storageServers.add(serverIP)

    def addContainers(self, serverIPs):
        self.storageServers.update(serverIPs)

    def deleteContainer(self, serverIP):
        self.storageServers.remove(serverIP)

    def __str__(self):
        """
        To string method
        """
        return f"FileName: {self.fileName}, FileSize: {self.fileSize}, FilePath: {self.filePath}\n" \
               f"Storage servers IPs: {self.storageServers}"

    def encode(self):
        """
        Return encoded data about file separated by delimiters
        """
        return f"{self.fileName}{DELIMITER}{self.fileSize}{DELIMITER}{self.filePath}".encode()


class StorageDemon:
    def __init__(self):
        self.serversFiles = dict()  # Dict {ServerIP:[FileInfo-s]}.
        self.fileDict = dict()  # Dict {(fileLocation):FileInfo}
        self.fileTree = FilesTree()

    def writeFile(self):
        pass

    def addFileToServer(self, server, fileInfo: FileInfo):
        # TODO
        if server in self.serversFiles:
            self.serversFiles[server].append(fileInfo)
        else:
            self.serversFiles[server] = [fileInfo]

    def delFileFromServer(self, server, fileInfo: FileInfo):
        self.serversFiles[server].remove(fileInfo)

    def createFile(self, fileInfo: FileInfo):
        servers = random.sample(StorageServers.keys(), REPLICAS)
        fileInfo.addContainers(servers)
        self.fileDict[fileInfo.fileLocation()] = fileInfo
        for server in servers:
            self.addFileToServer(server, fileInfo)
            print(f"Send CREATE request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"create" + B_DELIMITER + fileInfo.encode())

    def copyFile(self, fileInfo: FileInfo, newFileInfo: FileInfo):
        servers = self.fileDict[fileInfo.fileLocation()].storageServers
        newFileInfo.addContainers(servers)
        self.fileDict[newFileInfo.fileLocation()] = newFileInfo
        for server in servers:
            self.addFileToServer(server, newFileInfo)
            print(f"Send COPY request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"create" + B_DELIMITER + fileInfo.encode() +
                                                     B_DELIMITER + newFileInfo.encode())

    def delFile(self, fileInfo: FileInfo):
        trueFileInfo = self.fileDict[fileInfo.fileLocation()]
        servers = trueFileInfo.storageServers
        for server in servers:
            self.delFileFromServer(server, fileInfo)
            print(f"Send delete request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"delete" + B_DELIMITER + fileInfo.encode())

    def infoFile(self, fileInfo: FileInfo, clientSocket: socket.socket):
        trueFileInfo = self.fileDict[fileInfo.fileLocation()]
        clientSocket.send(trueFileInfo.encode())


class IPPropagator(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            print("New entity trying to find name server.")
            self.sock.sendto(b'Hello, new server', addr)


class HeartListener(Thread):
    def __init__(self, name: str, sock: socket.socket, ip: str):
        super().__init__(daemon=True)
        self.name = name
        self.sock = sock
        self.ip = ip

    def close(self):
        del StorageServers[self.ip]
        print(f"Storage server {self.name}(IP:{self.ip}) disconnected.")
        self.sock.close()

    def run(self):
        try:
            while self.sock.recv(BUFFER):
                sleep(3)
        except:
            pass
        finally:
            self.close()


class SSHeartbeatInitializer(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        serverID = 1
        while True:
            con, addr = self.sock.accept()
            serverIP = addr[0]
            SSName = f"SS_{serverID}"
            StorageServers[serverIP] = SSName
            print(f"Storage server {SSName}(IP:{serverIP}) connected.")
            serverID += 1
            HeartListener(SSName, con, serverIP).start()


class ClientMessenger(Thread):
    def __init__(self, name: str, sock: socket.socket, ip: str, demon: StorageDemon):
        super().__init__()
        self.name = name
        self.sock = sock
        self.ip = ip
        self.demon = demon

    def close(self):
        ClientIPs.remove(self.ip)
        print(f"Client {self.name}(IP:{self.ip}) disconnected.")
        self.sock.close()

    def run(self):
        try:
            while True:
                msg = self.sock.recv(BUFFER)
                if msg == b'':
                    sleep(1)
                    continue
                print(f'Client {self.name}(IP:{self.ip}) send a message: {msg.decode()}')
        except:
            pass
        finally:
            self.close()


class ClientWelcome(Thread):
    def __init__(self, sock: socket.socket, demon: StorageDemon):
        super().__init__(daemon=True)
        self.sock = sock
        self.demon = demon

    def run(self):
        clientID = 1
        while True:
            con, addr = self.sock.accept()
            clientIP = addr[0]
            ClientIPs.append(clientIP)
            clientName = f"CLIENT_{clientID}"
            print(f"Client {clientName}(IP:{clientIP}) connected.")
            clientID += 1
            ClientMessenger(clientName, con, clientIP, self.demon).start()


class ServerWelcome(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        while True:
            con, addr = self.sock.accept()
            serverIP = addr[0]
            serverName = StorageServers[serverIP]
            StorageServerMessageSockets[serverIP] = con
            print(f"Storage server {serverName}(IP:{serverIP}) establish messaging connection.")


def main():
    # UDP socket to meet new connections and provide them IP
    IPPropagationSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    IPPropagationSocket.bind(("", SERVER_WELCOME_PORT))
    IPPropagator(IPPropagationSocket).start()

    # TCP welcome socket for initializing Storage Servers heartbeats
    storageServerHeartbeatInitializer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storageServerHeartbeatInitializer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    storageServerHeartbeatInitializer.bind(('', SERVER_HEARTBEAT_PORT))  # Bind to specified port
    storageServerHeartbeatInitializer.listen()  # Enable connections
    SSHeartbeatInitializer(storageServerHeartbeatInitializer).start()

    # TCP welcome socket for message data about requests
    storageServerWelcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storageServerWelcomeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    storageServerWelcomeSocket.bind(('', SERVER_MESSAGE_PORT))
    storageServerWelcomeSocket.listen()
    ServerWelcome(storageServerWelcomeSocket).start()

    demon = StorageDemon()

    # TCP socket to initiate connections with Clients
    clientWelcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientWelcomeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clientWelcomeSocket.bind(("", CLIENT_MESSAGE_PORT))
    clientWelcomeSocket.listen()
    ClientWelcome(clientWelcomeSocket, demon).start()

    while True:
        pass


if __name__ == "__main__":
    main()
