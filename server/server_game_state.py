from queue import Queue, Empty
from shared.transmitted_data_formats import ClientInputDataFormat
import random

class ServerGameState:

    def __init__(self, players):
        self.players_states: list[ServerPlayerState] = players

    def update(self, time_delta, multiplier): #for test purposes only
        for player in self.players_states:
            player.level = multiplier
            player.pos[0] += time_delta * player.velocity[0] * multiplier
            if player.pos[0] > 200 or player.pos[0] < -200:
                player.velocity[0] *= -1
            
            if player.pos[1] < -300:
                player.pos[1] = -300
                player.velocity[1] = 0
                player.alive = False

            try:
                while not player.input_queue.empty():
                    if player.input_queue.get(block=False) == ClientInputDataFormat.JUMPED:
                        if player.is_on_ground:
                            player.velocity[1] = player.jump_force
                            player.is_on_ground = False
                        else:
                            player.velocity[1] = player.jump_force
            except Empty:
                pass
            
            if not player.is_on_ground:
                player.velocity[1] += player.gravity * time_delta
            
            player.pos[1] += player.velocity[1] * time_delta

            if player.pos[1] > 200:
                player.pos[1] = 200
                player.velocity[1] = 0
                player.is_on_ground = True

    def return_player_positions(self):
        return [{"id": p.id, "pos": p.pos.copy(), "alive": p.alive, "level": p.level} for p in self.players_states]


class ServerPlayerState:

    def __init__(self, id):
        self.level = 1
        self.input_queue: Queue = Queue()
        self.velocity = [200, 0]
        self.pos = [random.randint(-200, 200), 0]
        self.id = id
        self.alive = True
        self.gravity = 1200
        self.jump_force = -600
        self.is_on_ground = False
