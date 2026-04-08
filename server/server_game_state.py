from queue import Queue, Empty
from shared.transmitted_data_formats import ClientInputDataFormat

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
        return [player.pos for player in self.players_states]


class ServerPlayerState:

    def __init__(self):
        self.input_queue: Queue = Queue()
        self.velocity = [200, 0]
        self.pos = [0, 0]

