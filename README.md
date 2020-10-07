# Documentation how to launch and use the system

To start the system write:

```shell
docker-compose --compatibility up --build
```

It will create NameServer, 5 StorageServers and a client.

After that run client CLI by writing a command in client container:

```shell
python Client.py
```

You can use `help` command in the client CLI to get list of available commands.

# Architectural diagrams

## Overall architecture
![Architectual diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/ArchitectualDiagram.png?raw=true)

## Examples of communication between servers and clients

### System initialization
![Architectural diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/System%20start.gif)

### Writing a file from client
![Architectural diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/writeGIF.gif)

### Storage server failure

![Architectural diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/Server%20failure.gif)

# Description of communication protocols
#### Ports:

**<u>5000</u> : Providing NameServer IP**

​		Usage: Provide IP of the NameServer to new StorageServer or client

**<u>5001</u> : Heartbeat between NameServer and StorageServers**

​		Usage: Detect StorageServer failure or disconnect

**<u>5002</u> : Messaging between NameServer and StorageServer**

​		Usage: Send requests from NameServer to StorageServer. For example: create file.txt in folder /papka

**<u>5003</u> : Messaging between NameServer and client**

​		Usage: Send requests from client to NameServer. For example: check that folder /papka exists

**<u>5004</u> : File transfer from StorageServer to client and vice versa**

​		Usage: Send and receive file. Associated with write and read commands

**<u>5005</u> : Replication between StorageServers**

​		Usage: Send files from one of StorageServers to another when server failure occurs

#### Communication messages:

All details about communication messages : [[link]](https://docs.google.com/spreadsheets/d/1wfZ-HVIMUxCe-5NDjI15huDx1ye0SksVHZwvQx1hjPs/edit?usp=sharing)

Short description: 

All hosts send type of request and required information about the file or folder separated by predefined delimiter. 

For example:  to get information about file, client send message with request type "info",  file name and file path.

In addition, there are predefined  confirmation and error messages that help determine whether request is invalid.

For example: if client want read file that not exist on servers, nameserver send error message to client.

# Provable contribution of each team member
#### Team members and main tasks:

- **Vitaliy Korbashov** (v.korbashov@innopolis.university)

  - Implement StorageServers and make Docker files

- **Ruslan Muravev** (r.muravev@innopolis.university)

  - Implement NameServer

- **Anatoliy Baskakov** (a.baskakov@innopolis.university)

  - Implement client and CLI

  You can check GitHub Insights tab to view statistics about the work done on the project.