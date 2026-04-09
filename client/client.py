import sys
import os

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

SERVER_ADDRESS = ("127.0.0.1", 9999) # we will use localhost for now
UPDATE_RATE = 60 # these values need to be the same as values in server.py
DT = 1.0 / UPDATE_RATE

class ClientState(Enum):
    SEEKING_MATCH = 1 # confusing name. should be more like JOINING_LOBBY
    PREPARING_GAME = 2
    CONNECTED = 3

class ServerGameStateReceiver(threading.Thread): # should handle interrupting the connections

    def __init__(self, game_state_data_q, client_sock):
        super().__init__()
        self.s: socket.socket = client_sock
        self.game_state_data_queue: Queue = game_state_data_q
        self.id = None

    def run(self):
        while True:
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


class Client: # will hold reference to the client side game state and will order to update visuals

    def __init__(self):
        self.s: socket.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.game_state_data_queue: Queue = Queue()
        self.state = ClientState.SEEKING_MATCH
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

                t1 = time.perf_counter()
                acc = 0.0
                while True:
                    self.process_pygame_events()
                    t2 = time.perf_counter()
                    time_delta = t2 - t1
                    t1 = t2

                    acc += time_delta
                    if acc >= DT:
                        self.try_updating_local_game_state()
                        acc -= DT

    def find_a_match(self):
        command = MatchmakingFormingDataFormat.CLIENT_SEEKS_MATCH
        serialized_command = pickle.dumps(command)
        print(f"Looking for a lobby at address {SERVER_ADDRESS[0]}")
        self.s.sendto(serialized_command, SERVER_ADDRESS)

        data, server_addr = self.s.recvfrom(1024) # will block if it does not receive a response from server

        try:
            server_response: MatchmakingResponse = pickle.loads(data)
        except pickle.UnpicklingError:
            print("Client received corrupted response when trying to find a match!")
            return

        if not isinstance(server_response, MatchmakingResponse):
            return

        if server_addr == SERVER_ADDRESS and server_response.status == MatchmakingFormingDataFormat.FOUND_MATCH:
            print("Game has been found!")
            self.id = server_response.player_id
            self.state = ClientState.PREPARING_GAME

    def initialize_game(self):
        self.game = Game()
        self.conn = ServerGameStateReceiver(self.game_state_data_queue, self.s)
        self.conn.start()
        self.state = ClientState.CONNECTED

    def try_updating_local_game_state(self):
        try:
            last_state = None
            
            while not self.game_state_data_queue.empty():
                last_state = self.game_state_data_queue.get(block=False)

            if last_state:
                self.game.update_based_on_server_game_state(last_state, self.id)
        except Empty:
            print("Client tried updating his game state but game state queue was empty") # ideally, a client should never reach this kind of situation

    def process_pygame_events(self):
        for event in self.game.return_pygame_events():
            if event.type == pygame.constants.QUIT:
                exit(0) # harsh exit
            elif event.type == pygame.constants.KEYDOWN and event.key == pygame.constants.K_SPACE:
                self.send_user_input()

    def send_user_input(self):
        client_input: ClientInputDataFormat = ClientInputDataFormat.CHANGED_DIRECTION
        serialized_input = pickle.dumps(client_input)
        self.s.sendto(serialized_input, SERVER_ADDRESS)

if __name__ == "__main__":
    client = Client()

