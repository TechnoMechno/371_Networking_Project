import socket

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'
    port = 12345
    client_socket.connect((host, port))

    try:
        while True:
            message = ("Hi!")
            client_socket.send(message.encode())
            if message.lower() == 'exit':
                break
    finally:
        client_socket.close()

if __name__ == '__main__':
    start_client()
