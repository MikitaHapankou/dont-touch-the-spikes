# Don't Touch The Spikes - Multiplayer Arcade Game

A real-time multiplayer arcade game utilizing a client-server architecture. The project is built with Python and Pygame, relying on raw UDP sockets.

## Tech Stack
* Programming Language: Python 3.11+
* Graphics: Pygame
* Networking: UDP Sockets
* Deployment: systemd on VPS server, GitHub Actions

## Architecture

The project is modularized into distinct components to separate network logic from game rendering:

* **Server Component**
  * `server/server.py`: The network core of the server. It handles the matchmaking process, manages client connections, and asynchronously processes incoming UDP packets.
  * `server/server_game_state.py`: The game engine. It processes physics, including gravity, player velocity, wall collisions, and spike generation.
* **Client Component**
  * `client/client.py`: The network client. It receives server broadcast states and sends user input (e.g., jumps) back to the server.
  * `client/game.py`: Handles graphical rendering using Pygame. It draws the arena, player states, spikes, and end-game screens based on the data received from the server.
* **Shared Resources**
  * `shared/game_constants.py`: Contains global geometric and physical constants, such as arena width, player radius, and spike dimensions.
  * `shared/transmitted_data_formats.py`: Defines the data structures and Enum classes used for payload serialization via `pickle`.

## Usage Guide

### 1. Prerequisites
Ensure Python 3.11+ is installed. It is recommended to use a virtual environment to isolate project dependencies:
```
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies
```
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory of the project. This file is required to bind and connect to the correct network addresses. You can copy `example.env` as a starting config:
```
HOST=127.0.0.1
PORT=9999
```

### 3. Running the Game Locally
To test the game locally, you must run one instance of the server and the required number of clients (defined in `server/server.py`):
Start the server process:
```
cd server
python3 server.py
```

Start the client process:
```
cd client
python3 client/client.py
```
Start the second client process in a new terminal window. The server will automatically initiate the match once the required number of players have joined.

### CI/CD and Deployment
This repository is configured with a GitHub Actions workflow for continuous deployment.
Upon pushing to the main branch, the workflow connects to the remote VPS via SSH.
The script pulls the latest code, updates the Python virtual environment, and installs dependencies.
The deployment is finalized by restarting the game-server.service via systemd to apply changes with minimal downtime.