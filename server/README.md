# server.py

The first player will act as the server so we do not need a dedicated server,
then the other players will be clients.

When a client has a message that needs to be broadcasted, 
it will first send to the server first, and the the server will deal with the broadcasting.

## Functions Overview

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

