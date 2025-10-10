# 🍪 Cookie Grabber

<div align="center">

### *A Real-Time Multiplayer Cookie Collection Game*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-00979D?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![UDP](https://img.shields.io/badge/Protocol-UDP-orange?style=for-the-badge)](https://en.wikipedia.org/wiki/User_Datagram_Protocol)

</div>

---

## 🎬 Demo

<div align="center">

![Cookie Grabber Gameplay](demo_video.gif)

*Watch players compete in real-time to grab the most cookies!*

</div>

---

## 🎯 Overview

A fast-paced multiplayer game where players compete in real-time to collect the most cookies from a shared plate. Built to demonstrate **UDP networking**, **client-server architecture**, and **real-time game state synchronization**.

**Key Technical Features:**
- Real-time UDP socket communication for low-latency multiplayer
- Client-server architecture with centralized game state management
- Lobby system with player ready-up functionality
- Server-side collision detection and validation
- Thread-safe concurrent client and server operations

---

## 🛠️ Tech Stack

**Core:** Python 3.8+ • Pygame 2.0+ • UDP Sockets

**Architecture:** Client-Server Model • Threading • JSON Serialization • Event-Driven Design

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Pygame (`pip install pygame`)

### Run the Game
```bash
git clone https://github.com/TechnoMechno/371_Networking_Project.git
cd 371_Networking_Project
python game_main.py
```

---

## 🎮 How to Play

### Host a Game
1. Run `python game_main.py`
2. Click **"Host Game"** to start a server
3. Share your IP address with other players
4. Click **"Ready"** when all players have joined

### Join a Game
1. Run `python game_main.py`
2. Enter the host's IP address
3. Click **"Join Game"**
4. Click **"Ready"** to start

### Gameplay
- **Objective:** Collect more cookies than your opponents
- **Controls:** Left click to grab cookies from the plate
- **Cookie Types:**
  - 🍪 Regular Cookie: 1 point
  - ⭐ Star Cookie: 3 points (rare)

---

## 📁 Project Structure

```
371_Networking_Project/
├── 📂 game_code/              # Core game logic and entities
│   ├── config.py              # Game configuration and constants
│   ├── game.py                # Main game loop
│   ├── player.py              # Player entity
│   └── cookie_refactored.py   # Cookie entity
│
├── 📂 server2/                # Server-side implementation
│   ├── server_main.py         # Server entry point
│   ├── networking.py          # UDP server logic
│   └── GameStateManager.py    # Game state management
│
├── 📂 client2/                # Client-side implementation
│   ├── client_main.py         # Client entry point
│   ├── client_networking.py   # UDP client logic
│   ├── render.py              # Rendering engine
│   └── Button.py, TextBox.py  # UI components
│
└── game_main.py               # Main application entry point
```

---

## 💡 Technical Highlights

### Network Programming
- **UDP Protocol:** Implemented custom handshake protocol for connection validation
- **Packet Handling:** Managed packet loss and out-of-order delivery
- **State Sync:** JSON-based game state broadcasting to all clients

### Concurrent Programming
- Python threading for simultaneous client/server operations
- Thread-safe communication between network and game logic

### Game Architecture
- **Server Authority:** Centralized validation prevents cheating and desync
- **Collision Detection:** Server-side validation for cookie grabbing
- **State Management:** Enum-based system (LOBBY → PLAYING → GAME_OVER)

### Problem Solving
- **Race Conditions:** Server-side validation ensures only first valid request succeeds
- **Mid-Game Joins:** JOIN_CHECK handshake prevents joining during active games
- **Scalability:** Modular client-server design allows easy feature additions

---

## 🔮 Future Enhancements

- [ ] Power-ups and special abilities
- [ ] Leaderboard and persistent stats
- [ ] Multiple game modes (team play, time attack)
- [ ] NAT traversal for internet play
- [ ] Player authentication system

---

## 📄 License

This project is open source and available for educational purposes.

---
