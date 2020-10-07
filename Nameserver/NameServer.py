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

# TODO CHANGE
REPLICAS = 2

ERR_MSG = "NO"
B_ERR_MSG = b"NO"
CONFIRM_MSG = "YES"
B_CONFIRM_MSG = b"YES"

# Dict {ServerIP:ServerName}
StorageServers = {}
# Dict {ServerIP:ServerMessageSocket}
StorageServerMessageSockets = {}

ClientIPs = []


class FilesTree:
    def __init__(self):
        self.root = FolderNode("root", None)

    def getFolderByPath(self, path: str):
        path = path.split("/")
        currentDir = self.root
        for directory in path:
            if directory != "":
                currentDir = currentDir.getFolder(directory)
        return currentDir


# Folder
class FolderNode:
    def __init__(self, name: str, head):
        self.name = name
        self.files = []
        self.folders = []
        self.head = head

    def addFolder(self, node):
        self.folders.append(node)
        node.head = self

    def removeFolder(self, node):
        self.folders.remove(node)

    def getFolder(self, folderName):
        for folder in self.folders:
            if folder.name == folderName:
                return folder
        raise Exception

    def addFile(self, leafFile):
        self.files.append(leafFile)

    def removeFile(self, leafFile):
        self.files.remove(leafFile)

    def removeAllFiles(self):
        for file in self.files:
            self.files.remove(file)

    def isEmpty(self):
        return len(self.folders) == 0 and len(self.files) == 0

    def __str__(self):
        """
        String with all info about folders and files.
        """
        if len(self.folders) != 0:
            result = "│Folders:"
            for folder in self.folders:
                result += f"\n└──{folder.name}"
            result += "\n\n"
        else:
            result = "Directory does not contain any folder\n"
        if len(self.files) != 0:
            result += "│Files:"
            for fileInfo in self.files:
                result += f"\n└──{fileInfo.fileName}"
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

    def addContainer(self, serverIP: str):
        self.storageServers.add(serverIP)

    def addContainers(self, serverIPs: str):
        self.storageServers.update(serverIPs)

    def deleteContainer(self, serverIP: str):
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
        self.fileDict = dict()      # Dict {(fileLocation):FileInfo}
        self.fileTree = FilesTree()

    def addFileToServer(self, server, fileInfo: FileInfo):
        """
        Add file to serverFiles dictionary.
        Do not send the file.
        """
        if server in self.serversFiles:
            self.serversFiles[server].append(fileInfo)
        else:
            self.serversFiles[server] = [fileInfo]

    def delFileFromServer(self, server, fileInfo: FileInfo):
        """
        Remove file from serverFiles dictionary.
        Do not delete file from the server itself.
        """
        listOfFiles = self.serversFiles[server]
        listOfFiles.remove(fileInfo)

    def isFileExists(self, fileInfo: FileInfo):
        """
        Check whether the file exists as record in demon.
        """
        try:
            _ = self.fileDict[fileInfo.fileLocation()]
            return True
        except:
            return False

    def initialize(self, clientSocket: socket.socket):
        """
        Send the request to delete all files from storage servers.
        Purge all data about files.
        Receive information about the storage from servers and send that refactored to the client.
        """
        space = 0
        for serverSocket in StorageServerMessageSockets.values():
            # Let garbage collector manage it
            self.serversFiles = dict()
            self.fileDict = dict()
            self.fileTree = FilesTree()
            serverSocket.send(b"init")
            data = serverSocket.recv(BUFFER).decode().split(DELIMITER)
            serverSpace = int(data[1])
            space += serverSpace
        realSpace = space // REPLICAS // (2**20) // 8
        clientSocket.send(str(realSpace).encode())

    def createFile(self, fileInfo: FileInfo):
        """
        Send request to create files to the StorageServers.
        Add info about the file to the demon.
        If file already exist (same fileName and path), replace it with empty copy.
        """
        # Send create request only to servers with same file signature if it is exists
        if self.isFileExists(fileInfo):
            trueFileInfo: FileInfo = self.fileDict[fileInfo.fileLocation()]
            # Make it "empty"
            trueFileInfo.fileSize = 0
            servers = trueFileInfo.storageServers
            for server in servers:
                print(f"Send CREATE request to storage server with IP:{server}")
                StorageServerMessageSockets[server].send(b"create" + B_DELIMITER + fileInfo.encode())
            return
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

    def readFile(self, fileInfo: FileInfo, clientSocket: socket.socket):
        """
        Send file from storage server to client via informing each other about necessary info.
        If file does not exist, send error message to client.
        """
        if self.isFileExists(fileInfo):
            trueFileInfo = self.fileDict[fileInfo.fileLocation()]
            server = random.sample(trueFileInfo.storageServers, 1)[0]
            clientSocket.send(DELIMITER.join([server, str(trueFileInfo.fileSize)]).encode())
            print(f"Send READ to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"read" + B_DELIMITER + trueFileInfo.encode())
        else:
            print(f"No such file {fileInfo}")
            clientSocket.send(B_ERR_MSG)

    def writeFile(self, fileInfo: FileInfo, clientSocket: socket.socket):
        """
        Send file from client to storage server via informing each other about necessary info.
        Add record about file to demon.
        If file is already exists (same fileName and path), replace it with sent file.
        """
        # Send write request only to servers with same file signature if it is exists
        if self.isFileExists(fileInfo):
            trueFileInfo: FileInfo = self.fileDict[fileInfo.fileLocation()]
            trueFileInfo.fileSize = fileInfo.fileSize
            servers = trueFileInfo.storageServers
            for server in servers:
                print(f"Send CREATE request to storage server with IP:{server}")
                StorageServerMessageSockets[server].send(b"write" + B_DELIMITER + fileInfo.encode())
            clientSocket.send(DELIMITER.join(servers).encode())
            return
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
            StorageServerMessageSockets[server].send(b"write" + B_DELIMITER + fileInfo.encode())
        clientSocket.send(DELIMITER.join(servers).encode())

    def delFile(self, fileInfo: FileInfo):
        """
        Send file deletion request to StorageServers
        Purge info about that file from demon
        """
        # If file not exist => do not make anything
        if not self.isFileExists(fileInfo):
            return
        trueFileInfo = self.fileDict[fileInfo.fileLocation()]
        self.fileTree.getFolderByPath(trueFileInfo.filePath).removeFile(trueFileInfo)
        servers = trueFileInfo.storageServers
        for server in servers:
            self.delFileFromServer(server, trueFileInfo)
            print(f"Send delete request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"del" + B_DELIMITER + fileInfo.encode())
        del self.fileDict[trueFileInfo.fileLocation()]

    def infoFile(self, fileInfo: FileInfo, clientSocket: socket.socket):
        """
        Find file and send information about it to client
        """
        # In case of such file does not exist, send "File not found"
        if not self.isFileExists(fileInfo):
            clientSocket.send(b"File not found")
            return
        # Find file in demon storage
        trueFileInfo = self.fileDict[fileInfo.fileLocation()]
        # Send info about file
        clientSocket.send(trueFileInfo.__str__().encode())

    def copyFile(self, fileInfo: FileInfo, newFileInfo: FileInfo, clientSocket: socket.socket):
        """
        Send copy request to StorageServers with original file
        Add info about new copy to demon
        """
        # If file not exist, notify client about it
        if not self.isFileExists(fileInfo):
            clientSocket.send(B_ERR_MSG)
            return
        clientSocket.send(B_CONFIRM_MSG)
        # choose servers with such file
        servers = self.fileDict[fileInfo.fileLocation()].storageServers
        newFileInfo.addContainers(servers)
        trueFileSize = self.fileDict[fileInfo.fileLocation()].fileSize
        newFileInfo.fileSize = trueFileSize
        self.fileTree.getFolderByPath(newFileInfo.filePath).addFile(newFileInfo)
        self.fileDict[newFileInfo.fileLocation()] = newFileInfo
        for server in servers:
            self.addFileToServer(server, newFileInfo)
            print(f"Send COPY request to storage server with IP:{server}")
            StorageServerMessageSockets[server].send(b"copy" + B_DELIMITER + fileInfo.encode() +
                                                     B_DELIMITER + newFileInfo.encode())

    def moveFile(self, fileInfo: FileInfo, newFileInfo: FileInfo, clientSocket: socket.socket):
        """
        Call copy and delete method
        (@see copyFile and delFile)
        """
        self.copyFile(fileInfo, newFileInfo, clientSocket)
        self.delFile(fileInfo)

    def openDirectory(self, path: str, clientSocket: socket.socket):
        """
        Check whether directory exist.
        If directory exists, send B_CONFIRM_MSG to client.
        Send B_ERR_MSG otherwise.
        """
        try:
            self.fileTree.getFolderByPath(path)
            clientSocket.send(B_CONFIRM_MSG)
        except:
            clientSocket.send(B_ERR_MSG)

    def readDirectory(self, path, clientSocket: socket.socket):
        """
        Send information about files and directories in described folder to client.
        If file does not exist, send B_ERR_MSG to client
        """
        try:
            clientSocket.send(self.fileTree.getFolderByPath(path).__str__().encode())
        except:
            clientSocket.send(B_ERR_MSG)

    def makeDirectory(self, path: str, dirName: str, clientSocket: socket.socket):
        """
        Make directory in demon.
        If path is not correct, send B_ERR_MSG to client. (B_CONFIRM_MSG if it exist)
        """
        try:
            headDir = self.fileTree.getFolderByPath(path)
            if dirName in [fld.name for fld in headDir.folders]:
                pass  # IF directory exist => pass
            else:
                headDir.addFolder(FolderNode(dirName, headDir))
            clientSocket.send(B_CONFIRM_MSG)
        except:
            clientSocket.send(B_ERR_MSG)  # Source path does not exist

    def delDirectory(self, path):
        """
        Delete directory from demon.
        Send delete directory request to storage servers.
        """
        directory = self.fileTree.getFolderByPath(path)
        headDirectory = directory.head
        self.recursiveDelete(directory)
        headDirectory.removeFolder(directory)
        for serverSocket in StorageServerMessageSockets.values():
            serverSocket.send(b"deldir" + B_DELIMITER + path.encode())

    def recursiveDelete(self, folder: FolderNode):
        """
        Delete inside files and folders in specified folder via recursion
        """
        for subFolder in folder.folders:
            self.recursiveDelete(subFolder)
            folder.removeFolder(subFolder)
        for file in folder.files:
            for storageServer in file.storageServers:
                self.delFileFromServer(storageServer, file)
            del self.fileDict[file.fileLocation()]
        folder.removeAllFiles()

    def checkAndDelDirectory(self, path, clientSocket: socket.socket):
        """
        If target folder is empty, delete it.
        If target folder is not empty, ask user about confirmation and delete it if user agree.
        If target folder does not exist, send B_ERR_MSG to client.
        """
        try:
            if self.fileTree.getFolderByPath(path).isEmpty():
                clientSocket.send(b"folderEmpty")
                self.delDirectory(path)
            else:
                clientSocket.send(b"folderNotEmpty")
                while True:
                    response = clientSocket.recv(BUFFER)
                    if response != b"":
                        response = response.decode()
                        if response == "acceptDel":
                            self.delDirectory(path)
                            break
                        elif response == "denyDel":
                            break
                        else:
                            print(f"Unknown response: {response}")
                            break
        except:
            clientSocket.send(B_ERR_MSG)

    def handleServerClose(self, serverIP: str):
        """
        Send all files that was on specified server to another server without that file.
        """
        # Get information about all files that were on that server
        files = self.serversFiles[serverIP]
        print(f"ServerIP of disconnected server: {serverIP}")
        for file in files:
            print(f"FileInfo: {file}")
            # Find available servers to save information
            availableStorageServers = [*StorageServers]
            print(f"Available SS: {availableStorageServers}")
            for SS in file.storageServers:
                availableStorageServers.remove(SS)
            print(f"Available SS: {availableStorageServers}")
            # Delete information about storage server from fileInfo
            file.deleteContainer(serverIP)
            # Find server with file and server that can receive new replica
            serverSender: str = random.sample(file.storageServers, 1)[0]
            serverReceiver: str = random.sample(availableStorageServers, 1)[0]
            serverSenderSocket: socket.socket = StorageServerMessageSockets[serverSender]
            serverReceiverSocket: socket.socket = StorageServerMessageSockets[serverReceiver]
            print(f"Replicate from server {serverSender} to server {serverReceiver} of file {file}")
            # Send information about file and corresponding opponent server to storage servers
            serverSenderSocket.send(b"serverSend" + B_DELIMITER + serverReceiver.encode() + B_DELIMITER + file.encode())
            serverReceiverSocket.send(b"serverReceive" + B_DELIMITER + serverSender.encode()
                                      + B_DELIMITER + file.encode())
            self.addFileToServer(serverReceiver, file)
            file.addContainer(serverReceiver)
            sleep(0.1488)
        # Delete server from list of servers in demon
        del self.serversFiles[serverIP]


class IPPropagator(Thread):
    def __init__(self, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(BUFFER)
            print("New entity trying to find name server.")
            self.sock.sendto(b'Hello, new server', addr)


class HeartListener(Thread):
    def __init__(self, name: str, sock: socket.socket, ip: str, storageDemon: StorageDemon):
        super().__init__(daemon=True)
        self.name = name
        self.sock = sock
        self.ip = ip
        self.demon = storageDemon

    def close(self):
        print(f"Storage server {self.name}(IP:{self.ip}) disconnected.")
        self.demon.handleServerClose(self.ip)
        del StorageServers[self.ip]
        del StorageServerMessageSockets[self.ip]

        self.sock.close()

    def run(self):
        try:
            # Receive heartbeat
            while self.sock.recv(BUFFER):
                sleep(3)
        except:
            pass
        finally:
            self.close()


class SSHeartbeatInitializer(Thread):
    def __init__(self, sock: socket.socket, storageDemon: StorageDemon):
        super().__init__(daemon=True)
        self.sock = sock
        self.demon = storageDemon

    def run(self):
        serverID = 1
        while True:
            con, addr = self.sock.accept()
            serverIP = addr[0]
            SSName = f"SS_{serverID}"
            StorageServers[serverIP] = SSName
            print(f"Storage server {SSName}(IP:{serverIP}) connected.")
            serverID += 1
            HeartListener(SSName, con, serverIP, self.demon).start()


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
                print(f"Get request information {data} from client: {self.name}")
                req, meta = data[0], data[1:]
                if req == "write":
                    fileName = meta[0]
                    fileSize = int(meta[1])
                    filePath = meta[2]
                    fileInfo = FileInfo(fileName, filePath, fileSize)
                    self.demon.writeFile(fileInfo, self.sock)
                elif req == "init":
                    self.demon.initialize(self.sock)
                elif req == "del":
                    fileName = meta[0]
                    filePath = meta[1]
                    fileInfo = FileInfo(fileName, filePath, 0)
                    self.demon.delFile(fileInfo)
                elif req == "create":
                    fileName = meta[0]
                    filePath = meta[1]
                    fileInfo = FileInfo(fileName, filePath, 0)
                    self.demon.createFile(fileInfo)
                elif req == "read":
                    fileName = meta[0]
                    filePath = meta[1]
                    fileInfo = FileInfo(fileName, filePath, 0)
                    self.demon.readFile(fileInfo, self.sock)
                    pass
                elif req == "info":
                    fileName = meta[0]
                    filePath = meta[1]
                    fileInfo = FileInfo(fileName, filePath, 0)
                    self.demon.infoFile(fileInfo, self.sock)
                elif req == "copy":
                    fileName = meta[0]
                    filePath = meta[1]
                    newFileName = meta[2]
                    newFilePath = meta[3]
                    fileInfo = FileInfo(fileName, filePath, 0)
                    newFileInfo = FileInfo(newFileName, newFilePath, 0)
                    self.demon.copyFile(fileInfo, newFileInfo, self.sock)
                elif req == "move":
                    fileName = meta[0]
                    filePath = meta[1]
                    newFileName = meta[2]
                    newFilePath = meta[3]
                    fileInfo = FileInfo(fileName, filePath, 0)
                    newFileInfo = FileInfo(newFileName, newFilePath, 0)
                    self.demon.moveFile(fileInfo, newFileInfo, self.sock)
                elif req == "ls":
                    path = meta[0]
                    self.demon.readDirectory(path, self.sock)
                elif req == "mkdir":
                    dirName = meta[0]
                    path = meta[1]
                    self.demon.makeDirectory(path, dirName, self.sock)
                elif req == "del_dir":
                    path = meta[0]
                    self.demon.checkAndDelDirectory(path=path, clientSocket=self.sock)
                elif req == "cd":
                    path = meta[0]
                    self.demon.openDirectory(path, self.sock)
                else:
                    print(f"Unknown request: {req}")
                    continue
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

    # Initialize storage demon
    demon = StorageDemon()

    # TCP welcome socket for initializing Storage Servers heartbeats
    storageServerHeartbeatInitializer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storageServerHeartbeatInitializer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    storageServerHeartbeatInitializer.bind(('', SERVER_HEARTBEAT_PORT))  # Bind to specified port
    storageServerHeartbeatInitializer.listen()  # Enable connections
    SSHeartbeatInitializer(storageServerHeartbeatInitializer, demon).start()

    # TCP welcome socket for message data about requests with Storage Servers
    storageServerWelcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    storageServerWelcomeSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    storageServerWelcomeSocket.bind(('', SERVER_MESSAGE_PORT))
    storageServerWelcomeSocket.listen()
    ServerWelcome(storageServerWelcomeSocket).start()

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
