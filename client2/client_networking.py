import socket, json, threading, time

"""
client_networking.py - Handles UDP networking for the client.
This module creates a UDP socket for communication with the server, sends update messages,
and listens for server broadcasts on a separate thread.
"""

class ClientNetworking:
    #Initialize the networking client with server connection details.
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.connect((server_ip, server_port))
        self.udp_socket.setblocking(False)
        self.client_running = True
        self.receive_callbacks = []

    #Sends a message object to the server after converting to json
    def send_message(self, message_obj):
        try:
            self.udp_socket.send(json.dumps(message_obj).encode())
        except Exception as e:
            print("Send error:", e)
    
    #function for when messages are received
    def add_receive_callback(self, callback):
        self.receive_callbacks.append(callback)
    
    #Main loop for receiving incoming messages and callbacks
    def receive_loop(self):
        while self.client_running:
            try:
                data, addr = self.udp_socket.recvfrom(8192)
                msg_obj = json.loads(data.decode())
                for cb in self.receive_callbacks:
                    cb(msg_obj)
            except BlockingIOError:
                time.sleep(0.01)
            except Exception as e:
                print("Receive error:", e)
                time.sleep(0.01)
    
    #Starts a thread to listen for incoming messages
    def start_receiving(self):
        thread = threading.Thread(target=self.receive_loop, daemon=True)
        thread.start()
    
    #Handles shutdown of the thread and closes the socket connection.
    def shutdown(self):
        self.client_running = False
        self.udp_socket.close()

