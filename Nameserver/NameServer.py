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
        self.root = FolderNode("root")

    def getFolderByPath(self, path: str):
        # TODO CHECK
        path = path.split("/")
        currentDir = self.root
        for directory in path:
            currentDir = currentDir.getFolder(directory)
        return currentDir


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

    def isEmpty(self):
        return len(self.folders) == 0 and len(self.files) == 0

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

    def writeFile(self, fileInfo: FileInfo, clientSocket: socket.socket):
        # choose random servers to handle request
        servers = random.sample(StorageServers.keys(), REPLICAS)
        # add list of servers as containers of information about file
        fileInfo.addContainers(servers)
        # add file in fileTree
        #TODO NE RABOTAET
        #self.fileTree.getFolderByPath(fileInfo.filePath).addFile(fileInfo)
        # add file to fileDict
        self.fileDict[fileInfo.fileLocation()] = fileInfo
        for server in servers:
            # add file to servers dict-s
            self.addFileToServer(server, fileInfo)
        clientSocket.send(DELIMITER.join(servers).encode())

    def addFileToServer(self, server, fileInfo: FileInfo):
        """
        Add file to serverFiles dictionary
        Do not send the file
        """
        if server in self.serversFiles:
            self.serversFiles[server].append(fileInfo)
        else:
            self.serversFiles[server] = [fileInfo]

    def delFileFromServer(self, server, fileInfo: FileInfo):
        """
        Remove file from serverFiles dictionary
        Do not delete file from the server itself
        """
        self.serversFiles[server].remove(fileInfo)

    def createFile(self, fileInfo: FileInfo):
        # choose random servers to handle request
        servers = random.sample(StorageServers.keys(), REPLICAS)
        # add list of servers as containers of information about file
        fileInfo.addContainers(servers)
        # add file in fileTree
        self.fileTree.getFolderByPath(fileInfo.filePath).addFile(fileInfo)
        # add file to fileDict
        self.fileDict[fileInfo.fileLocation()] = fileInfo
        for server in servers:
            # add file to servers dict-s
            self.addFileToServer(server, fileInfo)
            print(f"Send CREATE request to storage server with IP:{server}")
            # send request
            StorageServerMessageSockets[server].send(b"create" + B_DELIMITER + fileInfo.encode())

    def copyFile(self, fileInfo: FileInfo, newFileInfo: FileInfo):
        # choose servers with such file
        servers = self.fileDict[fileInfo.fileLocation()].storageServers
        newFileInfo.addContainers(servers)
        self.fileTree.getFolderByPath(newFileInfo.filePath).addFile(newFileInfo)
        self.fileDict[newFileInfo.fileLocation()] = newFileInfo
        for server in servers:
            self.addFileToServer(server, newFileInfo)
            print(f"Send COPY request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"copy" + B_DELIMITER + fileInfo.encode() +
                                                     B_DELIMITER + newFileInfo.encode())

    def delFile(self, fileInfo: FileInfo):
        trueFileInfo = self.fileDict[fileInfo.fileLocation()]
        self.fileTree.getFolderByPath(trueFileInfo.filePath).removeFile(trueFileInfo)
        servers = trueFileInfo.storageServers
        for server in servers:
            self.delFileFromServer(server, fileInfo)
            print(f"Send delete request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"delete" + B_DELIMITER + fileInfo.encode())

    def infoFile(self, fileInfo: FileInfo, clientSocket: socket.socket):
        trueFileInfo = self.fileDict[fileInfo.fileLocation()]
        clientSocket.send(trueFileInfo.encode())

    def moveFile(self, fileInfo: FileInfo, newFileInfo: FileInfo):
        self.copyFile(fileInfo, newFileInfo)
        self.delFile(fileInfo)

    @staticmethod
    def initialize(self):
        for serverSocket in StorageServerMessageSockets.values():
            serverSocket.send(b"init")

    def readDirectory(self, path, clientSocket: socket.socket):
        clientSocket.send(self.fileTree.getFolderByPath(path).__str__().encode())

    def delDirectory(self, path):
        directory = self.fileTree.getFolderByPath(path)
        for serverSocket in StorageServerMessageSockets.values():
            serverSocket.send(b"delDirectory" + path.encode())

    def checkAndDelDirectory(self, path, clientSocket: socket.socket):
        if self.fileTree.getFolderByPath(path).isEmpty():
            self.delDirectory(path)
        else:
            clientSocket.send(b"Ebat ti?")


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
                data = msg.decode().split(DELIMITER)
                req, meta = data[0], data[1:]
                if req == "write":
                    fileName = meta[0]
                    fileSize = int(meta[1])
                    filePath = meta[2]
                    fileInfo = FileInfo(fileName, filePath, fileSize)
                    self.demon.writeFile(fileInfo, self.sock)
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
