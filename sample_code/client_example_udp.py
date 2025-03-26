import pygame
import socket
import threading
import json
import time

# Define global shared state variables updated by the receive thread:
# - state: Stores target positions from the server in a dictionary with two keys:
#   'squares' (mapping square IDs to [x, y] positions) and 'mouses' (mapping player IDs to [x, y] positions)
# - state_lock: A threading lock to prevent data conflicts when multiple threads access 'state'
# - player_id: Unique ID assigned to this client by the server (starts as None)

state = {'squares': {}, 'mouses': {}}  # Target positions
state_lock = threading.Lock()  # Lock to synchronize access to 'state'
player_id = None  # Will be set by the server

# Dictionaries for smoothed (interpolated) positions used in rendering:
# - displayed_squares: Current positions of squares drawn on the screen
# - displayed_mouses: Current positions of mouse cursors drawn on the screen
displayed_squares = {}  # Format: {square_id: [x, y]}
displayed_mouses = {}   # Format: {player_id: [x, y]}

# Tracks which square this client is dragging (None if not dragging)
local_dragged_square = None

def lerp(a, b, t):
    """
    Linearly interpolate between two values.
    Parameters:
    - a: Starting value
    - b: Target value
    - t: Interpolation factor (0.0 = fully at a, 1.0 = fully at b)
    Returns: Interpolated value between a and b
    """
    return a + (b - a) * t  # Move from 'a' toward 'b' by fraction 't'

def lerp_pos(pos_a, pos_b, t):
    """
    Interpolate between two [x, y] positions.
    Parameters:
    - pos_a: Starting position [x, y]
    - pos_b: Target position [x, y]
    - t: Interpolation factor
    Returns: New [x, y] position between pos_a and pos_b
    """
    return [lerp(a, b, t) for a, b in zip(pos_a, pos_b)]  # Apply lerp to x and y coordinates

def receive_thread(client_socket):
    """
    Continuously receive messages from the server in a separate thread.
    Parameters:
    - client_socket: UDP socket for communication
    """
    global state, player_id  # Access global variables to update them
    while True:  # Infinite loop to keep listening
        try:
            # Receive up to 4096 bytes from the server and decode to a string
            # In UDP, each recv call gets one complete datagram
            data = client_socket.recv(4096).decode()
            if not data:  # If no data received, skip to next iteration
                continue
            data_obj = json.loads(data)  # Parse JSON string into a Python dictionary
            if data_obj['type'] == 'assign_id':  # If server assigns this client's ID
                player_id = data_obj['player_id']  # Store the assigned ID
            elif data_obj['type'] == 'update_positions':  # If server sends position updates
                with state_lock:  # Lock 'state' to safely modify it
                    # Update 'squares' and 'mouses' with new positions
                    # Convert string keys to integers (JSON converts all keys to strings)
                    state['squares'] = {int(k): v for k, v in data_obj['squares'].items()}
                    state['mouses'] = {int(k): v for k, v in data_obj['mouses'].items()}
        except Exception as e:  # Handle any errors during receiving
            print(f"Receive error: {e}")  # Log the error
            break  # Exit the loop if an error occurs

def main():
    """
    Set up and run the game client, managing input, rendering, and server communication.
    """
    global displayed_squares, displayed_mouses, local_dragged_square  # Access global variables

    # Define server address as a tuple (IP, port)
    server_address = ('127.0.0.1', 5555)
    # Create a UDP socket (AF_INET = IPv4, SOCK_DGRAM = UDP)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # "Connect" to the server address for simpler send/recv calls (UDP-specific shortcut)
    client_socket.connect(server_address)

    def send_message(msg_obj):
        """
        Send a message to the server.
        Parameters:
        - msg_obj: Dictionary containing the message data
        """
        message = json.dumps(msg_obj)  # Convert dictionary to JSON string
        client_socket.send(message.encode())  # Encode to bytes and send via UDP

    # Launch the receive thread to listen for server messages
    # daemon=True ensures it stops when the main program exits
    threading.Thread(target=receive_thread, args=(client_socket,), daemon=True).start()

    # Set up Pygame and the game window
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Create an 800x600 pixel window
    pygame.display.set_caption("Multiplayer Square Dragging Game (UDP)")  # Window title
    clock = pygame.time.Clock()  # Clock to control frame rate

    running = True  # Flag to control the main loop
    while running:  # Main game loop
        # Handle Pygame events (user inputs)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # User clicked the close button
                running = False  # Stop the game loop
            elif event.type == pygame.MOUSEMOTION:  # Mouse moved
                pos = list(pygame.mouse.get_pos())  # Get current mouse position as [x, y]
                # Send mouse position to server
                send_message({'type': 'mouse_move', 'position': pos})
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Mouse button pressed
                pos = pygame.mouse.get_pos()  # Get click position
                with state_lock:  # Lock 'state' to safely read it
                    for square_id, square_pos in state['squares'].items():  # Check each square
                        # If click is within a 50x50 square
                        if (square_pos[0] <= pos[0] <= square_pos[0] + 50 and
                            square_pos[1] <= pos[1] <= square_pos[1] + 50):
                            # Notify server to start dragging this square
                            send_message({'type': 'start_drag', 'square_id': square_id})
                            local_dragged_square = square_id  # Track locally
                            break  # Stop checking other squares
            elif event.type == pygame.MOUSEBUTTONUP:  # Mouse button released
                # Notify server to stop dragging
                send_message({'type': 'stop_drag'})
                local_dragged_square = None  # Clear local tracking

        # Smoothly update displayed positions toward server-provided targets
        with state_lock:  # Lock 'state' to safely read it
            for key, target in state['squares'].items():  # For each square
                # Use faster interpolation (0.8) if this client is dragging, else slower (0.2)
                factor = 0.8 if key == local_dragged_square else 0.2
                if key in displayed_squares:  # If square already has a displayed position
                    # Interpolate toward the target position
                    displayed_squares[key] = lerp_pos(displayed_squares[key], target, factor)
                else:  # New square, set directly to target
                    displayed_squares[key] = target
            for key, target in state['mouses'].items():  # For each mouse cursor
                if key in displayed_mouses:  # If mouse cursor has a displayed position
                    # Interpolate toward the target position (always factor 0.2)
                    displayed_mouses[key] = lerp_pos(displayed_mouses[key], target, 0.2)
                else:  # New mouse cursor, set directly to target
                    displayed_mouses[key] = target

        # Render the game state
        screen.fill((255, 255, 255))  # Clear screen with white
        for pos in displayed_squares.values():  # Draw all squares
            pygame.draw.rect(screen, (0, 0, 255), (*pos, 50, 50))  
        for pl_id, pos in displayed_mouses.items():  
            # Red for this player's cursor, green for others
            color = (255, 0, 0) if pl_id == player_id else (0, 255, 0)
            pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), 5)  # 5-pixel circle

        pygame.display.flip()  # Update the screen with the new frame
        clock.tick(60)  # Cap frame rate at 60 FPS

    # Clean up when exiting
    client_socket.close()  # Close the UDP socket
    pygame.quit()  # Shut down Pygame

# Run the main function if this script is executed directly
if __name__ == '__main__':
    main()