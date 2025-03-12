import socket
#import mongo
import client_server
#from pymongo import MongoClient
import threading
import multiGame
import time

#MAX PLAYER COUNT = 2

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 3001
client_count = 0
server_address = ("localhost", PORT)
client_data = {
}
client_order = []
client_sockets = []
compareScores = ""
data_lock = threading.Lock()
data = ''
player = 0
done = 0
def handle_client(client_socket,client_address):
    global client_data, player, client_count, data, done
     
    with data_lock:
            client_order.append(client_address)
    
    try:
        client_count = client_count + 1
        client_sockets.append(client_socket)
        
    except Exception as e:
        print(f"Error in handle_client: {e}")
        
    try:
        
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received from {client_socket}: {data}")
            val = data.decode()
            print("Player 1", client_order[0])
            print("Player 2", client_order[1])
            if val == "COLLISION":
                 print("SERVER RECEIVED COLLISION FROM: ", client_address)
                 done = done + 1
                 print("Done:", done)
                 print("client data len:", len(client_data))
                 if done == 2:
                    print("Current Client:", client_address)
                    i = 1
                    for score in client_data.values():
                        print("i: ", i)
                        if i == 1:
                            player1 = score
                            i = i + 1
                        elif i == 2:
                            player2 = score
                            i = i + 1
                        else:
                            print("No more players")
                
                    try:
                        
                        print("Player 1 Scored: ",player1)
                        print("Player 2 Scored: ", player2)
                    
                        
                        if player1 > player2:
                            print("1")
                            winner = "Player 1 Wins!"
                        elif player1 < player2:
                            print("2")
                            winner = "Player 2 Wins!"
                        elif player1 == player2:
                            print("3")
                            winner = "It's a Tie!"
                        else:
                            print("4")
                            winner = "No Winner!"
                        broadcast(winner)
                        time.sleep(5)
                        server_socket.close()
                    except Exception as e:
                        print(f"An error occurred: {e}")
                    
                
            else:
                score = val
                
                client_data[client_address] = float(score)
                print(f"Updated score for {client_address}: {client_data[client_address]}")
    finally:
        print("I ran")
        #client_socket.close()
def is_server_running():
    try:
        with socket.create_connection(("localhost", 3001), timeout=1):
            # If connection is successful, server is running
            return True
    except (ConnectionRefusedError, socket.timeout):
        # If connection is refused or times out, server is not running
        return False

def broadcast(message):
    global client_sockets
    to_remove = []

    for cs in client_sockets:
        try:
            cs.send(message.encode())
        except Exception as e:
            print(f"Error broadcasting to client: {e}")
            to_remove.append(cs)
            
            
    # Only remove and close sockets that are problematic
    for cs in to_remove:
        if cs in client_sockets:
            print("I ran and removed")
            client_sockets.remove(cs)
            cs.close()
        

    # Do not clear the entire list of client sockets here
    # client_sockets.clear()


def isStarted():
    try:
        with socket.create_connection(server_address):
            return True
    except ConnectionRefusedError:
        return False
running = True
start = 0
def stopServer():
    global running
    running = False

def serverMain():
    global client_count, player, data, start, client_data, client_order
    player = 0
    ply = 0
    print("Server Main Initialization")
    print("--------------------")
    
    if isStarted():
        client_server.client_main()
    else: 
        server_socket.bind(server_address)

        # Listen for incoming connections   
        server_socket.listen(3)

        print('Server is listening on', server_address)
        
        while running:
            try:
                #print("clients connected: ", len(client_sockets))
                if client_count < 3:
                    client_socket, client_address = server_socket.accept()
                     # Processes multiple clients data from the client
                    client_thread = threading.Thread(target=handle_client, args=(client_socket,client_address))
                    client_thread.start()
                    
                    print('Connected to', client_address)
                    ply += 1
                    if ply > 2:
                        ply = 2
                    message = f"You are Player {ply}"
                    client_socket.send(message.encode())
                    winner = "Error No winner"
                   
                    
                
                #print(collision_result)f
                if client_count == 3 and start == 0:
                    start += 1
                    startGame = "Start"
                    broadcast(startGame)
                
                
                
              
                    
                        
            except socket.timeout:
                pass

if __name__ == "__main__":
    serverMain()
