# Documentation how to launch and use the system
```shell
docker-compose --compatibility up --build
```

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
Ports:

5000 : Providing name server IP  

5001 : Heartbeat between NameServer and StorageServers  

5002 : Messaging between NameServer and StorageServer

5003 : Messaging between NameServer and client

5004 : File transfer from StorageServer to client and vice versa

5005 : Replication between StorageServers

# Provable contribution of each team member
### list of good bois

1. VItaliy
2. RUSLAN
3. TOLYA
