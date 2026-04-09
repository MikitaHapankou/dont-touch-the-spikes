from queue import Queue, Empty
from shared.transmitted_data_formats import ClientInputDataFormat
from shared.game_constants import *
import random

class ServerGameState:

    def __init__(self, players):
        self.players_states: list[ServerPlayerState] = players

    def update(self, time_delta, multiplier): #for test purposes only
        for player in self.players_states:
            if not player.alive: continue
            player.level = multiplier
            player.pos[0] += time_delta * player.velocity[0] * multiplier

            self.handle_possible_wall_collision(player)
            self.handle_possible_death(player)
            self.process_players_inputs(player)
            self.move_player(player, time_delta)


    def return_player_positions(self):
        return [{"id": p.id, "pos": p.pos.copy(), "alive": p.alive, "level": p.level} for p in self.players_states]

    def handle_possible_wall_collision(self, player):
        if player.pos[0] > ARENA_WIDTH / 2 or player.pos[0] < -ARENA_WIDTH / 2:
            player.velocity[0] *= -1

    def handle_possible_death(self, player):
        if player.pos[1] < -ARENA_HEIGHT / 2 or player.pos[1] > ARENA_HEIGHT / 2:
            player.pos[1] = -300 # hacky way to make player dead
            player.velocity[1] = 0
            player.alive = False

    def move_player(self, player, time_delta):
        if not player.is_on_ground:
            player.velocity[1] += player.gravity * time_delta
        player.pos[1] += player.velocity[1] * time_delta

    def process_players_inputs(self, player):
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
