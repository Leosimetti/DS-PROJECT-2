# Documentation how to launch and use the system
```shell
docker-compose --compatibility up --build
```

# Architectural diagrams

## Overall architecture
![Architectual diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/ArchitectualDiagram.png?raw=true)

## Storage server failure
![Architectual diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/Server%20failure.gif)

## System initialization
![Architectual diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/System%20start.gif)

## Writing a file from client
![Architectual diagram](https://github.com/Leosimetti/DS-PROJECT-2/blob/main/writeGIF.gif)

# Description of communication protocols
Ports:

5000 : Providing name server IP  

5001 : Heartbeat between NameServer and StorageServers  

5002 : Messaging between NameServer and StorageServer

5003 : Messaging with clients  

5004 : File transfer from SS to client and vice versa

5005 : Replication between SS
# Provable contribution of each team member
### list of good bois

1. VItaliy
2. RUSLAN
3. TOLYA
