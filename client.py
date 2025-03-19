import sys
import select
import socket
import threading
import pygame
from game import Game  # Your Pygame game class
from config import BACKGROUND_COLOR
from ui import draw_plate, draw_pancakes, draw_scores
from server.shared import game_state

# --- Network Configuration ---
HOST = 'localhost'
TCP_PORT = 5555
UDP_PORT = 5556

# Global mode flag and score variable.
mode = "TCP"
network_score = 0
start_udp_mode = False

def tcp_receive(tcp_sock):
    global start_udp_mode
    while True:
        try:
            message = tcp_sock.recv(1024).decode().strip()
            if not message:
                break
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
            if message.startswith("Score:"):
                try:
                    network_score = int(message.split(":")[1].strip())
                    # Print the updated score when received.
                    print("Updated score:", network_score)
                except ValueError:
                    pass
        except Exception as e:
            print("UDP receive error:", e)
            break

def udp_mode():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', 0))
    udp_sock.sendto("register".encode(), (HOST, UDP_PORT))
    
    threading.Thread(target=udp_receive, args=(udp_sock,), daemon=True).start()
    
    game = Game()  
    running = True
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
        draw_pancakes(game.screen, game.pancakes)
        draw_scores(game.screen, network_score)
        pygame.display.flip()
        game.clock.tick(60)
    
    pygame.quit()
    udp_sock.close()

def main():
    global start_udp_mode
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((HOST, TCP_PORT))
    
    threading.Thread(target=tcp_receive, args=(tcp_sock,), daemon=True).start()
    
    print("Connected via TCP. Waiting in lobby...")
    # Non-blocking lobby loop:
    while True:
        if start_udp_mode:
            break
        ready, _, _ = select.select([sys.stdin], [], [], 0.1)
        if ready:
            user_input = sys.stdin.readline().strip()
            if user_input:
                try:
                    tcp_sock.send(user_input.encode())
                except Exception as e:
                    print("TCP send error:", e)
                    break
                if user_input.lower() == "quit":
                    break
    
    tcp_sock.close()
    udp_mode()
    print("Disconnected from the server.")

if __name__ == '__main__':
    main()
