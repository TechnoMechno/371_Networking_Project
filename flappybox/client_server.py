import socket
import multiGame
import displayMatchResult
data = ""
compareScores = "" 
score = 0
collided = False
client_socket = ''
winner = "1"
def send_collision_to_server():
    global client_socket
    #Send a collision notification to the server.
    try:
        client_socket.send("COLLISION".encode())
    except Exception as e:
        print(f"Error sending collision to server: {e}")
        
def send_score_to_server(scored):
    global client_socket
    #Send a socre notification to the server.
    try:
        val = str(scored)
        client_socket.send(val.encode())
    except Exception as e:
        print(f"Error sending collision to server: {e}")
def client_main():
    global compareScores, score, client_socket, winner
    # Client Socket is here
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connects to the server
    server_address = ('127.0.0.1', 3001)
    client_socket.connect(server_address)
    
    
    while True:
        scored = str(multiGame.getScore())
        score = scored
        print("Collided: ",collided)
        try:
            
            data = client_socket.recv(1024).decode()
            
            print('Received:', data)
            if data == "Start":
                multiGame.gameStart = data
            elif data == "Player 1 Wins!":
                displayMatchResult.gameWinner(data)
                winner = data
                compareScores = "Done"
                client_socket.close()
                break
            elif data == "Player 2 Wins!":
                displayMatchResult.gameWinner(data)
                winner = data
                compareScores = "Done"
                client_socket.close()
                break
            elif data == "It's a Tie!":
                displayMatchResult.gameWinner(data)
                winner = data
                compareScores = "Done"
                client_socket.close()
                break
            
        except Exception as e:
             print(f"error in client server: {e}")
def getResult():
    return data

def getWinner():
    return winner

if __name__ == "__main__":
    client_main()
