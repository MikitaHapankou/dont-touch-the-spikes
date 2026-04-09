import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import queue
import socket
import pickle
import threading
import time
from queue import Queue
from enum import Enum
from server_game_state import ServerPlayerState, ServerGameState
from shared.transmitted_data_formats import GameStateBroadcastFormat, MatchmakingFormingDataFormat, ClientInputDataFormat, MatchmakingResponse

SERVER_ADDRESS = ("127.0.0.1", 9999)
UPDATE_RATE = 60
DT = 1.0 / UPDATE_RATE

NUMBER_OF_PLAYERS = 2


class ServerState(Enum): # surely more states will come along the way
    GATHERING_PLAYERS = 1
    PREPARING_THE_GAME = 2
    PLAYING_OUT_THE_GAME = 3


class ClientInputReceiver(threading.Thread):

    def __init__(self, client_addr, server_sock, client_q):
        super().__init__()
        self.s: socket.socket = server_sock
        self.client_addr = client_addr
        self.client_queues: list[Queue] = client_q

    def run(self):
        while self.is_alive():
            data, sender_addr = self.s.recvfrom(1024)
            if sender_addr in self.client_addr:
                try:
                    client_input: ClientInputDataFormat = pickle.loads(data)
                    self.client_queues[sender_addr[0]].put(client_input, block=False) # queue allegedly is thread safe
                    print(f"Player received user input. Player address is {sender_addr[0]}")
                except queue.Full:
                    print(f"Connection handler failed at putting received data into player's queue. Players address is {sender_addr[0]}")
                except pickle.UnpicklingError:
                    print(f"Server received corrupted players input. Players address is {sender_addr[0]}")


class GameStateBroadcaster(threading.Thread): # unnecessary

    def __init__(self, client_addr, server_sock, unsend_game_states_queues):
        super().__init__()
        self.s: socket.socket = server_sock
        self.client_addr = client_addr
        self.unsend_game_states_queues: Queue = unsend_game_states_queues

    def run(self):
        while self.is_alive():
            game_state = self.unsend_game_states_queues.get()
            serialized_game_state = pickle.dumps(game_state)
            for addr in self.client_addr:
                self.s.sendto(serialized_game_state, addr)


class Server: # for now server is designed to hold only one game session at once

    def __init__(self):
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        self.clients = []
        self.client_conn_handler = None
        self.broadcaster = None
        self.game_state = None
        self.game_states_to_send_queue: Queue = Queue()
        self.state = ServerState.GATHERING_PLAYERS
        self.server_loop()

    def server_loop(self):
        while True:
            if self.state == ServerState.GATHERING_PLAYERS:
                self.listen_for_join_requests()
            elif self.state == ServerState.PREPARING_THE_GAME:
                self.prepare_the_game()
            elif self.state == ServerState.PLAYING_OUT_THE_GAME:
                self.play_out_the_game()

    def listen_for_join_requests(self):
        while True:
            data, client_addr = self.server_socket.recvfrom(1024)

            try:
                client_request: MatchmakingFormingDataFormat = pickle.loads(data)
            except pickle.UnpicklingError:
                print("Server received corrupted client request when forming a match")
                return

            if not isinstance(client_request, MatchmakingFormingDataFormat):
                return

            if client_request == MatchmakingFormingDataFormat.CLIENT_SEEKS_MATCH:
                self.clients.append(client_addr)
                response = MatchmakingResponse(MatchmakingFormingDataFormat.FOUND_MATCH, len(self.clients))
                serialized_response = pickle.dumps(response)
                self.server_socket.sendto(serialized_response, client_addr)

            if len(self.clients) >= NUMBER_OF_PLAYERS:
                self.state = ServerState.PREPARING_THE_GAME
                return # we have a set of players so we move on

    def prepare_the_game(self):
        buffs = {}
        players_states = []
        for i, client in enumerate(self.clients): 
            player_state = ServerPlayerState(i + 1)
            players_states.append(player_state)
            buffs[client[0]] = player_state.input_queue

        self.game_state = ServerGameState(players_states)
        self.client_conn_handler = ClientInputReceiver(self.clients, self.server_socket, buffs)
        self.client_conn_handler.start()
        self.broadcaster = GameStateBroadcaster(self.clients, self.server_socket, self.game_states_to_send_queue)
        self.broadcaster.start()
        self.state = ServerState.PLAYING_OUT_THE_GAME

    def play_out_the_game(self): # this way of updating will do for now
        t1 = time.perf_counter()
        acc = 0.0
        while True:
            t2 = time.perf_counter()
            time_delta = t2 - t1
            t1 = t2
            acc += time_delta

            if acc >= DT:
                self.game_state.update(DT)
                game_data = GameStateBroadcastFormat(self.game_state.return_player_positions())
                try:
                    self.game_states_to_send_queue.put(game_data, block=False)  # queue allegedly is thread safe
                except queue.Full:
                    print("Broadcaster queue is full!")
                acc -= DT

if __name__ == "__main__":
    server = Server()
