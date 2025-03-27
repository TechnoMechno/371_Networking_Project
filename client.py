import sys
import select
import socket
import threading
import pygame
from game import Game         
from config import BACKGROUND_COLOR
from ui import draw_plate, draw_cookies, draw_interface
from shared import GameState

HOST = '172.105.106.139'
TCP_PORT = 5555
UDP_PORT = 5556

mode = "TCP"
network_score = 0
start_udp_mode = False
is_first_player = True  # Because only the first player should have access to start the game.

def tcp_receive(tcp_sock):
    global start_udp_mode, is_first_player
    while True:
        try:
            message = tcp_sock.recv(1024).decode().strip()
            if not message:
                break
            # check if server is sending a player number
            # ideally, for server to send "player 1" for the first player
            if message.lower().startswith("player"):
                parts = message.lower.split()
                if len(parts) >= 2 and parts[1] == "1":
                    is_first_player = True
                    print("First player")
                else:
                    is_first_player = False
                    print("Not first player")
            if message.lower() == "game has started":
                start_udp_mode = True
        except Exception as e:
            break

def udp_receive(udp_sock):
    global network_score
    while True:
        try:
            data, _ = udp_sock.recvfrom(1024)
            message = data.decode().strip()
            # When a score update is received, print the same cookie message.
            if message.startswith("Score:"):
                try:
                    network_score = int(message.split(":")[1].strip())
                    print("Cookie collected! New score:", network_score)
                except ValueError:
                    pass
        except Exception as e:
            print("UDP receive error:", e)
            break

def udp_mode():
    # Create UDP socket and bind to an ephemeral port.
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', 0))
    udp_sock.sendto("register".encode(), (HOST, UDP_PORT))
    
    threading.Thread(target=udp_receive, args=(udp_sock,), daemon=True).start()
    
    # Initialize and run the game.
    game = Game()  
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    udp_sock.sendto("cookie".encode(), (HOST, UDP_PORT))
                elif event.key == pygame.K_ESCAPE:
                    udp_sock.sendto("quit".encode(), (HOST, UDP_PORT))
                    running = False
        
        game.screen.fill(BACKGROUND_COLOR)
        draw_plate(game.screen)
        draw_cookies(game.screen, game.pancakes)
        draw_interface(game.screen, network_score)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    udp_sock.close()

def main():
    global start_udp_mode
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((HOST, TCP_PORT))
    
    threading.Thread(target=tcp_receive, args=(tcp_sock,), daemon=True).start()


    input_buffer = []

    # Thread for collecting input without blocking the main thread
    def input_thread():
        while not start_udp_mode:
            try:
                line = input()
                input_buffer.append(line)
            except EOFError:
                break

    # Start input collection
    input_handler = threading.Thread(target=input_thread, daemon=True)
    input_handler.start()
    
    # Non-blocking lobby loop:
    try:
        while not start_udp_mode:
            # Process any inputs collected by the input thread
            if input_buffer:
                user_input = input_buffer.pop(0)

                # Allowing the "start" command only for the first player
                if user_input.lower() == "start":
                    if is_first_player:
                        tcp_sock.send(user_input.encode())
                        print("starting game")
                    else:
                        print("wait for first player to start the game")
                        continue
                else: 
                    try:
                        tcp_sock.send(user_input.encode())
                        print(f"You sent: {user_input}")
                    except Exception as e:
                        print(f"TCP send error: {e}")
                        break
                        
                if user_input.lower() == "quit":
                    break

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Ensure sockets are properly closed
        try:
            tcp_sock.close()
        except:
            pass

    if start_udp_mode:
        udp_mode()
                    
    tcp_sock.close()
    udp_mode()
    print("Disconnected from the server.")

if __name__ == '__main__':
    main()

