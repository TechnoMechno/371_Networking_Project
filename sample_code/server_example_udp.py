
import socket
import threading
import time
import json

players = {}   # Format: {player_id: (ip_address, port)}
squares = {0: [100, 100], 1: [200, 200], 2: [300, 300], 3: [400, 400], 4: [500, 500]}  # Initial square positions
mouses = {}    # Format: {player_id: [x, y]}
dragging = {}  # Format: {square_id: player_id}
next_player_id = 0  # Start assigning player IDs from 0
data_lock = threading.Lock()  # Create a lock object for thread safety

def handle_message(message, addr, server_socket):
    """
    Process messages sent from clients to the server.
    Parameters:
    - message: The raw string message received from a client
    - addr: The client's network address as a tuple (IP, port)
    - server_socket: The UDP socket object used to send and receive data
    """
    # Use the global next_player_id variable to assign new IDs
    global next_player_id

    # Try to convert the raw message string into a JSON object
    try:
        data_obj = json.loads(message)  # Parse the message into a Python dictionary
    except Exception as e:  # Catch any errors during JSON parsing
        print(f"JSON error: {e}")  # Print the error message if parsing fails
        return  # Exit the function if the message can't be understood

    # Lock shared data to prevent conflicts between threads
    with data_lock:
        # Check if this client's address is new (not already in the players dictionary)
        if addr not in players.values():
            # Assign the next available player ID to this new client
            player_id = next_player_id
            next_player_id += 1  # Increment the counter for the next new player
            players[player_id] = addr  # Store the client's address with their ID
            mouses[player_id] = [0, 0]  # Set the new player's mouse position to (0, 0) initially
            # Create a message to tell the client their assigned player ID
            assign_message = json.dumps({'type': 'assign_id', 'player_id': player_id})
            # Send the message back to the client over UDP
            server_socket.sendto(assign_message.encode(), addr)
        else:
            # If the client is already known, find their existing player ID
            player_id = None  # Start with no ID found
            for pid, a in players.items():  # Loop through all players
                if a == addr:  # Match the address
                    player_id = pid  # Set the matching player ID
                    break  # Exit the loop once found
        # If no player ID was found (unexpected), exit the function
        if player_id is None:
            return

        # Handle different types of messages from the client
        if data_obj['type'] == 'mouse_move':  # If the message is about mouse movement
            mouses[player_id] = data_obj['position']  # Update the player's mouse position
        elif data_obj['type'] == 'start_drag':  # If the message is to start dragging a square
            square_id = data_obj['square_id']  # Get the ID of the square to drag
            if square_id not in dragging:  # Check if no one else is dragging this square
                dragging[square_id] = player_id  # Assign this player as the one dragging the square
        elif data_obj['type'] == 'stop_drag':  # If the message is to stop dragging
            for sq_id, pl_id in list(dragging.items()):  # Loop through all dragging entries
                if pl_id == player_id:  # Find squares this player was dragging
                    del dragging[sq_id]  # Remove the dragging entry

def main():
    """
    Set up and run the game server, handling connections and game updates.
    """
    # Create a UDP socket using IPv4 (AF_INET) and UDP protocol (SOCK_DGRAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the local address 127.0.0.1 (localhost) and port 5555
    server_socket.bind(('127.0.0.1', 5555))
    print("Server started on UDP port 5555")  # Confirm the server is running

    def receive_loop():
        """
        Run in a separate thread to continuously listen for client messages.
        """
        while True:  # Keep running forever
            try:
                # Wait for incoming data (up to 4096 bytes) and get the sender's address
                data, addr = server_socket.recvfrom(4096)
                message = data.decode()  # Convert the received bytes into a string
                # Pass the message to the handler function
                handle_message(message, addr, server_socket)
            except Exception as e:  # Catch any errors during receiving
                print(f"Receive error: {e}")  # Print the error message

    # Start the receive_loop function in a new thread
    # daemon=True means it stops when the main program exits
    threading.Thread(target=receive_loop, daemon=True).start()

    # Main game loop to update and broadcast the game state
    while True:  # Run forever
        
        # Lock shared data to safely update it
        with data_lock:
            # Update the position of each square being dragged
            for square_id, player_id in dragging.items():  # Loop through dragging entries
                if player_id in mouses:  # Check if the dragging player has a mouse position
                    squares[square_id] = mouses[player_id]  # Move the square to the player's mouse

            # Create a message with the current game state to send to all clients
            update_message = {
                'type': 'update_positions',  # Indicate this is a position update
                # Convert square IDs to strings for JSON and include their positions
                'squares': {str(k): v for k, v in squares.items()},
                # Convert player IDs to strings for JSON and include their mouse positions
                'mouses': {str(k): v for k, v in mouses.items()}
            }
            message_json = json.dumps(update_message)  # Convert the message to a JSON string
            message_bytes = message_json.encode()  # Convert the JSON string to bytes

            # Send the update to all connected players
            for pid, addr in players.items():  # Loop through all players
                try:
                    # Send the update message to this player's address via UDP
                    server_socket.sendto(message_bytes, addr)
                except Exception as e:  # Catch errors (e.g., client disconnected)
                    print(f"Error sending to player {pid}: {e}")  # Report the error
                    del players[pid]  # Remove the player from the players dictionary
                    if pid in mouses:  # If they had a mouse position
                        del mouses[pid]  # Remove their mouse position
                    # Remove any squares they were dragging
                    for sq_id, pl_id in list(dragging.items()):
                        if pl_id == pid:  # Find squares this player was dragging
                            del dragging[sq_id]  # Stop tracking the dragging

        # Pause for 1/60th of a second to aim for 60 updates per second (60 FPS)
        time.sleep(1/60)

# Check if this script is being run directly (not imported)
if __name__ == '__main__':
    main()  # Start the server by calling the main function