from queue import Queue, Empty
from shared.transmitted_data_formats import ClientInputDataFormat
import random

class ServerGameState:

    def __init__(self, players):
        self.players_states: list[ServerPlayerState] = players

    def update(self, time_delta): #for test purposes only
        for player in self.players_states:
            player.pos[0] += time_delta * player.velocity[0]
            if player.pos[0] > 200 or player.pos[0] < -200:
                player.velocity[0] *= -1
            try:
                if player.input_queue.get(block=False) == ClientInputDataFormat.CHANGED_DIRECTION:
                    player.velocity[0] *= -1
            except Empty:
                pass


    def return_player_positions(self):
        return [{"id": p.id, "pos": p.pos.copy()} for p in self.players_states]


class ServerPlayerState:

    def __init__(self, id):
        self.input_queue: Queue = Queue()
        self.velocity = [200, 0]
        self.pos = [random.randint(-200, 200), 0]
        self.id = id

