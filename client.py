import socket
import threading
import sys

def listen_for_messages(client_socket):
    """
    Listens for messages from the server and prints them.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                print("Disconnected from server.")
                break
            print(message)
        except Exception as e:
            print("Error receiving data:", e)
            break

    client_socket.close()
    sys.exit()

def main():
    server_ip = "localhost"
    server_port = 5555  

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((server_ip, server_port))
        print(f"Connected to server at {server_ip}:{server_port}")

        server_message = client_socket.recv(1024).decode("utf-8").strip()

        # If the server is full, exit
        if server_message == "Game is full!":
            print("Game is full! Cannot join.")
            client_socket.close()
            return
        
        print(server_message) 
        
    except Exception as e:
        print("Could not connect to server:", e)
        return

    thread = threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True)
    thread.start()

    while True:
        try:
            message = input()
            if message.lower() == "quit":
                print("Quitting the game!")
                client_socket.send(message.encode("utf-8"))
                break
            elif message.lower() == "take pancake":
                print("You took a pancake!")
                client_socket.send(message.encode("utf-8"))
            client_socket.send(message.encode("utf-8")) 
        except KeyboardInterrupt:
            print("\nExiting...")
            client_socket.send("quit".encode("utf-8"))
            break

    client_socket.close()


if __name__ == '__main__':
    main()
