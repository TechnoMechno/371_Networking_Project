# basic_udp_client.py
import socket

UDP_IP = "127.0.0.1"      # The server's address (localhost)
UDP_PORT = 5005           # The port that the server is listening on
MESSAGE = "Hello, server!"

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Optionally set a timeout so recv doesn't block forever
sock.settimeout(2)

print(f"Sending message: {MESSAGE}")
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

# Try to receive a response (if the server sends one)
try:
    data, server = sock.recvfrom(4096)  # Buffer size is 4096 bytes
    print("Received response from server:", data.decode())
except socket.timeout:
    print("No response received from server.")

sock.close()