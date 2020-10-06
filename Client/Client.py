import socket
from threading import Thread
import random
import os
import re
from time import sleep
import sys
import math

BUFFER = 1024

SERVER_WELCOME_PORT = 5000
CLIENT_MESSAGE_PORT = 5002
FILE_TRANSFER_PORT = 5004

DELIMITER = "?CON?"
B_DELIMITER = b"?CON?"

ERR_MSG = "NO"
B_ERR_MSG = b"NO"
CONFIRM_MSG = "YES"
B_CONFIRM_MSG = b"YES"

class UnknownCommandException(Exception):

    pass


class Client():

    # Find and connect to the Namenode
    def __init__(self):
        # Find name server
        nameServerIP = self.findNameServer()
        # Establish connection
        nameServerMessengerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        nameServerMessengerSocket.connect((nameServerIP, CLIENT_MESSAGE_PORT))

        self.soc = nameServerMessengerSocket
        self.curDir = "/"

    def findNameServer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(b'Client try to find name server', ('<broadcast>', SERVER_WELCOME_PORT))
        data, addr = s.recvfrom(BUFFER)
        print(f'Name server found: {addr}')
        return addr[0]
    
    def askConfirmation(self, msg):
        print(f"{msg} [y/n] ", end="")
        ans = ""
        while True:
            ans = input()
            if ans in ["Yes", "yes", "y", "Y"]:
                return True
            if ans in ["No", "no", "n", "N"]:
                return False
            else:
                print(f"{msg} [y/n] ", end="")
                continue
    
    # Wait for response and, possibly, abort execution if it takes too long
    # TODO does not handle buffer overflow
    def getResponse(self, sock):
        failed_attempts = 0
        while True:
            # If server does not respond for too long, promt user
            if failed_attempts == 300:
                if not self.askConfirmation("No response from server. Wait more?"):
                    main()
                    return None
                failed_attempts = 0

            response = sock.recv(BUFFER).decode()
            if response == "":
                failed_attempts += 1
                sleep(0.01)
            else:
                return response
    
    # Extract full path and filename from relative path
    def parsePath(self, path):
        full_path = self.getFullPath(path)
        return os.path.split(full_path)

    # Convert relative path into full path
    def getFullPath(self, path):
        if path.startswith("/"):
            return path
        
        if path.startswith("./"):
            path = path[2:]
        
        return os.path.join(self.curDir, path)

    # Initialize the client storage on a new system
    # Removes all existing files in the DFS root directory and returns available size
    def init(self):
        self.soc.send("init".encode())

        print(f"Total free space: {self.soc.recv(BUFFER).decode()} Mb")
        # NOTE: I think it should ask for confirmation

    # Create a new empty file at specified location
    def create(self, filename):

        path, filename = self.parsePath(filename)
        msg = DELIMITER.join(["create", filename, path])
        self.soc.send(msg.encode())


    # Download a file from the DFS
    def read(self, filename, saveAs):

        # Resolve name collisions if there are any
        if os.path.exists(saveAs):
            print(f"File {saveAs} already exists")
            if not self.askConfirmation("Do you want to overwrite it?"):
                # If user does not want to overwrite a file,
                # Then abort execution
                return
        
        path, filename = self.parsePath(filename)

        msg = DELIMITER.join(["read", filename, path])
        self.soc.send(msg.encode())
        # Wait for data about servers
        response = self.soc.recv(BUFFER)
        while response == b"":
            response = self.soc.recv(BUFFER)
        response = response.decode()
        if response == ERR_MSG:
            print(f"No such file found")
            return
        server, size = response.split(DELIMITER)
        size = int(size)

        sock = socket.socket()
        sock.connect((server, FILE_TRANSFER_PORT))
        sleep(1)

        with open(saveAs, "wb") as f:
            for i in range(math.ceil(size/BUFFER)):
                rcv = sock.recv(BUFFER)
                if rcv:
                    f.write(rcv)
                else:
                    print("File download complete!!")
                    break

    def _write(self, sock, filename, size):
        print("!!!Connected to server!!!")  # if it is not displayed ==> OOF

        # Counter initialization
        sas = 0
        pr_digit = '0'

        # Read/Send
        with open(filename, "rb") as f:
            for i in range(size):
                snd = f.read(BUFFER)
                if snd:

                    # To make output less annoying
                    msg = str(round(sas / float(size) * 100))
                    if pr_digit != msg[0] and round(sas / float(size) * 100) > 9:
                        print(msg, " %")
                        pr_digit = msg[0]

                    sas += BUFFER
                    sock.sendall(snd)
                else:
                    print("Transfer complete!!")
                    break

    # Upload filesrc to DFS as filename
    def write(self, filesrc, filename=None):
        
        if not os.path.exists(filesrc):
            print(f"File {filesrc} not found")
            return
        
        # If second argument was not provided,
        # Use source's filename
        if filename == None:
            _, filename = os.path.split(filesrc)
        
        size = os.path.getsize(filesrc)
        path, filename = self.parsePath(filename)

        # Send metadata first
        msg = DELIMITER.join(["write", filename, str(size), path])
        self.soc.send(msg.encode())

        # Wait for data about servers
        response = self.soc.recv(BUFFER).decode()
        servers = response.split(DELIMITER)

        # Send to this server
        print(f"IPS are {servers}")
        sleep(1)
        for ip in servers:
            sock = socket.socket()
            sock.connect((ip, FILE_TRANSFER_PORT))
            self._write(sock, filesrc, size)
            print(f"Completed transfer to IP {ip}")

    # Delete given file from DFS
    def delete(self, filename):

        path, filename = self.parsePath(filename)

        msg = DELIMITER.join(["del", filename, path])
        self.soc.send(msg.encode())

    # Get information about the file (any useful information - size, node id, etc.)
    def info(self, filename):

        path, filename = self.parsePath(filename)

        msg = DELIMITER.join(["info", filename, path])
        self.soc.send(msg.encode())

        response = self.getResponse(self.soc)
        if response != None:
            # TODO parse file info
            print(response)

    # Copy file from src to dest
    def copy(self, src, dest):

        filepath, filename = self.parsePath(src)
        new_filepath, new_filename = self.parsePath(dest)

        msg = DELIMITER.join(["copy", filename, filepath, new_filename, new_filepath])
        self.soc.send(msg.encode())

    # Move file from src to dest
    def move(self, src, dest):

        filepath, filename = self.parsePath(src)
        new_filepath, new_filename = self.parsePath(dest)

        msg = DELIMITER.join(["move", filename, filepath, new_filename, new_filepath])
        self.soc.send(msg.encode())

    # Change GayErectory
    def open_dir(self, path):

        path = self.getFullPath(path)

        msg = DELIMITER.join(["cd", path])
        self.soc.send(msg.encode())

        response = self.getResponse(self.soc)
        if response == None:
            return

        if response == ERR_MSG:
            print("No such directory")
        elif response == CONFIRM_MSG:
            self.curDir = path
            print(f"Directory successfully changed. You are currently at\n{path}")
        else:
            print("Smert'")
            

    # Get list of files stored in the directory
    def read_dir(self, path):

        path = self.getFullPath(path)

        msg = DELIMITER.join(["ls", path])
        self.soc.send(msg.encode())

        response = self.getResponse(self.soc)
        if response == None:
            return

        if response == ERR_MSG:
            print("No such directory")
        else:
            print("\t".join(response.split(DELIMITER)))

    # Create a new directory
    def make_dir(self, dir_name):

        path, dir_name = self.parsePath(dir_name)

        msg = DELIMITER.join(["mkdir", dir_name, path])
        self.soc.send(msg.encode())

    # Delete directory
    # If directory contains files, will prompt user for confirmation before deletion.
    def del_dir(self, dir_name):
        
        full_dir_name = self.getFullPath(dir_name)

        msg = DELIMITER.join(["del_dir", full_dir_name])
        self.soc.send(msg.encode())

        response = self.getResponse(self.soc)
        if response == None:
            return

        if response == "folderNotEmpty":
            print("Directory contains some files")
            if self.askConfirmation("Are you sure you want to delete it?"):
                self.soc.send("acceptDel".encode())
            else:
                self.soc.send("denyDel".encode())
                return
        

    def parseCommand(self, command):
        try:
            command = command.split()

            args = command[1:]
            command = command[0]
        except IndexError:
            args = []
        

        if command == "init":
            self.init()

        elif command == "create" or command == "make":
            self.create(args[0])

        elif command == "read" or command == "get":
            self.read(args[0], args[1])

        elif command == "write" or command == "put":
            if len(args) == 1:
                self.write(args[0])
            else:
                self.write(args[0], args[1])

        elif command in ["delete", "del", "rm"]:
            self.delete(args[0])

        elif command == "info":
            self.info(args[0])

        elif command == "copy" or command == "cp":
            self.copy(args[0], args[1])

        elif command == "move" or command == "mv":
            self.move(args[0], args[1])

        elif command == "open" or command == "cd":
            self.open_dir(args[0])

        elif command == "read_dir" or command == "ls":
            self.read_dir(args[0])

        elif command == "make_directory" or command == "mkdir":
            self.make_dir(args[0])

        elif command == "delete_directory" or command == "del_dir":
            self.del_dir(args[0])
        
        elif command == "help":
            self.print_help()

        else:
            raise UnknownCommandException


def print_help():
    # TODO
    print("List of available commands:\n")
    print("init\tInitialize the client storage on a new system; removes any existing file in the dfs root directory and returns available size.")
    print("create filename\tCreates a new empty file.")
    print("read filesrc filedest\tDownload a file from the DFS")
    print("write filesrc filedest\tUpload a file to the DFS")
    print("delete filename\tDelete given file from DFS")
    print("info filename\tProvide information about the file (size, node id, etc.)")
    print("copy filename\tCreate a copy of a file")
    print("move filesrc filedest\tMove a file to the specified path")
    print("open path\tChange directory")
    print("read\tReturn list of files, which are stored in the directory")
    print("mkdir dirname\tCreate a new directory")
    print("del_dir dirname\tDelete directory. If the directory contains files, asks for confirmation before deletion")


def main():
    # In case user only querried help, do not execute anything else
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print_help()
            return 0
    print("For help, run this with --help (-h) argument")

    client = Client()

    while True:
        command = input("->")
        try:
            client.parseCommand(command)
        except UnknownCommandException:
            print(f"NO SUCH COMMAND: {command} , you IDIOT FUCK YOU BITCH")
            continue
        except IndexError:
            print("Provide more arguments")
        # nameServerMessengerSocket.send(b"Hello")
        # sleep(3)


if __name__ == '__main__':
    main()
