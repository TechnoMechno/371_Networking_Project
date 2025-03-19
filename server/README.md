# Multiplayer Game Server

The first player will act as the server so we do not need a dedicated server,
then the other players will be clients.

When a client has a message that needs to be broadcasted, 
it will first send to the server first, and the the server will deal with the broadcasting.

## Project Files 
- `server.py`: main server script handling player connections, game logic, and message broadcasting, also the very first player.
- `shared.py`: contains shared definitions to be used across both server and clients
- `cookie_game.py` (not being used right now): to hold the actual cookie game that can be used throughout the players

## How to Run

### Running the server (first player)

Start the server by executing:
```bash 
python server.py
```

The clients (currently in the root directory) can also be run by:
```bash
python client.py
``` 
after switching to root directory.

## Game Flow

### Lobby Phase (TCP)
- Players join and leave lobby using TCP
- Must have at least two players to start the game

### Game Phase (UDP)
- Real-time interactions using UDP
- (Temporarily to test networking with the actual game aspect) Players collect cookies to increase the global score

### How to Play
(Temporarily)
Press space and watch funny number to up.

## Networking Functions Summary

Purely definitions for each of the networking functions used.

### socket.socket(...)
```python
server_socket = socket.socket(family, type, protocol)
```

where
- family: the address fmaily (IPv4 or IPV6)
- type: the sockt type(TCP or UDP)
- protocol (optional)

common socket families
- socket.AF_INET    (IPv4 default)
- socket.AF_INET6   (IPv6)

common socket types
- socket.SOCK_STREAM    (TCP)
- socket.SOCK_DGRAM     (UDP)

### server_socket.bind(...)
a server must bind to an address and listen for incoming connections
```py
server_socket.bind({IP}, {PORT})
```

### server_socket.listen(...)
```py
server_socket.listen(backlog)
```

where 
- backlog: maximum number of unaccepted connections the system will allow before refusing new ones

### data, addr = server_socket.recvfrom(...)
```py
data, addr = server_Socket.recvfrom(bufsize)
```

where
- bufsize: maximum number of bytes to receive in one call
- data: received message as a bytes object
- addr: tuple containing the server's IP address and port

