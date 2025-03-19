from enum import Enum

class GameState(Enum):
    WAITING = "waiting"
    COUNTDOWN = "countdown"
    IN_PROGRESS = "in_progress"
    DISPLAY_RESULTS = "display_results"
    GAME_OVER = "game_over"
                     # List of tuples: (name, ip, udp_port) 
game_state = GameState.WAITING