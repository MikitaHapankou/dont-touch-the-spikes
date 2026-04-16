import sys
import os
from dotenv import load_dotenv
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import threading
import pickle
import time
import pygame.constants
from queue import Queue, Full, Empty
from enum import Enum
from shared.transmitted_data_formats import GameStateBroadcastFormat, MatchmakingFormingDataFormat, ClientInputDataFormat, MatchmakingResponse
from game import Game

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

SERVER_ADDRESS = (HOST, PORT)
UPDATE_RATE = 60
DT = 1.0 / UPDATE_RATE

class ClientState(Enum):
    SEEKING_MATCH = 1
    PREPARING_GAME = 2
    CONNECTED = 3

class ServerGameStateReceiver(threading.Thread):

    def __init__(self, game_state_data_q, client_sock):
        super().__init__()
        self.s: socket.socket = client_sock
        self.game_state_data_queue: Queue = game_state_data_q
        self.id = None

    def run(self):
        while True:
            try:
                self.s.settimeout(1.0)
                data, server_addr = self.s.recvfrom(1024)
                
                if server_addr != SERVER_ADDRESS:
                    return

                try:
                    game_state: GameStateBroadcastFormat = pickle.loads(data)
                    self.game_state_data_queue.put(game_state, block=False)
                except pickle.UnpicklingError:
                    print("Client received corrupted game state data!")
                except Full:
                    print("Client game_state buffer is full!")
            except socket.timeout:
                print("Waiting for server...")
                continue 
            except Exception as e:
                print(f"Critical client error: {e}")
                break


class Client:

    def __init__(self):
        self.client_socket: socket.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.game_state_data_queue: Queue = Queue()
        self.state = ClientState.SEEKING_MATCH
        self.client_id = None
        self.game = None
        self.conn = None
        self.client_loop()

    def client_loop(self):
        while True:
            if self.state == ClientState.SEEKING_MATCH:
                self.find_a_match()
            elif self.state == ClientState.PREPARING_GAME:
                self.initialize_game()
            elif self.state == ClientState.CONNECTED:
                self.game_loop()

    def game_loop(self):
        t1 = time.perf_counter()
        acc = 0.0
        while True:
            self.process_pygame_events()
            t2 = time.perf_counter()
            time_delta = t2 - t1
            t1 = t2

            acc += time_delta
            if acc >= DT:
                is_dead = self.try_updating_local_game_state()
                if is_dead == 1:
                    time.sleep(5)
                    os._exit(0)
                acc -= DT

    def find_a_match(self):
        command = MatchmakingFormingDataFormat.CLIENT_SEEKS_MATCH
        serialized_command = pickle.dumps(command)

        print("\nCLIENT: sending join request to", SERVER_ADDRESS)

        self.client_socket.sendto(serialized_command, SERVER_ADDRESS)

        self.client_socket.settimeout(5)

        try:
            data, server_addr = self.client_socket.recvfrom(1024)
        except Exception as e:
            print("NO RESPONSE FROM SERVER:", e)
            return

        print("CLIENT: response received from", server_addr)

        try:
            server_response = pickle.loads(data)
            print("CLIENT DECODED:", server_response)
        except Exception as e:
            print("BAD RESPONSE:", e)
            return

        if server_response.status == MatchmakingFormingDataFormat.FOUND_MATCH:
            print("MATCH FOUND")
            self.client_id = server_response.player_id
            self.state = ClientState.PREPARING_GAME

    def initialize_game(self):
        self.game = Game()
        self.conn = ServerGameStateReceiver(self.game_state_data_queue, self.client_socket)
        self.conn.start()
        self.state = ClientState.CONNECTED

    def try_updating_local_game_state(self):
        try:
            last_state = None
            while not self.game_state_data_queue.empty():
                last_state = self.game_state_data_queue.get(block=False)

            if last_state:
                is_alive = self.game.update_based_on_server_game_state(last_state, self.client_id)
                if not is_alive:
                    time.sleep(5)
                    os._exit(0)
        except Empty:
            print("Client tried updating his game state but game state queue was empty")

    def process_pygame_events(self):
        for event in self.game.return_pygame_events():
            if event.type == pygame.constants.KEYDOWN and event.key == pygame.constants.K_SPACE:
                self.send_user_input()
            elif event.type == pygame.constants.KEYDOWN and event.key == pygame.constants.K_q or event.type == pygame.constants.QUIT:
                self.client_socket.close()
                pygame.display.quit()
                pygame.quit()
                os._exit(0)

    def send_user_input(self):
        client_input: ClientInputDataFormat = ClientInputDataFormat.JUMPED
        serialized_input = pickle.dumps(client_input)
        self.client_socket.sendto(serialized_input, SERVER_ADDRESS)

if __name__ == "__main__":
    client = Client()

