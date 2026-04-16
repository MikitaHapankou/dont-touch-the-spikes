from queue import Queue, Empty
from shared.transmitted_data_formats import ClientInputDataFormat
from shared.game_constants import *
import random
import math

class ServerGameState:

    def __init__(self, players):
        self.players_states: list[ServerPlayerState] = players
        self.right_spikes_positions: list = []
        self.left_spikes_positions: list = []
        self.randomize_spike_locations()

    def update(self, time_delta, multiplier):
        alive = 0
        for player in self.players_states:
            if not player.alive:
                continue
            
            alive += 1

            player.level = multiplier
            player.pos[0] += time_delta * (player.velocity[0] + player.velocity[0] * multiplier * 0.4)

            self.handle_possible_wall_collision(player)
            self.handle_possible_floor_collision(player)
            self.process_players_inputs(player)
            self.move_player(player, time_delta)
            self.handle_spike_collision(player)
        
        if alive == 1:
            for player in self.players_states:
                player.endGame = True

        return alive
    
    def return_player_positions(self):
        return [{"id": p.id, "pos": p.pos.copy(), "alive": p.alive, "level": p.level, "endGame": p.endGame}
                for p in self.players_states]

    def return_spike_locations(self):
        return list(self.left_spikes_positions), list(self.right_spikes_positions)

    def handle_possible_wall_collision(self, player):
        if player.pos[0] + PLAYER_RADIUS > ARENA_WIDTH / 2:
            player.pos[0] = ARENA_WIDTH / 2 - PLAYER_RADIUS
            player.velocity[0] = -abs(player.velocity[0])
            self.randomize_spike_locations(side="left")

        elif player.pos[0] - PLAYER_RADIUS < -ARENA_WIDTH / 2:
            player.pos[0] = -ARENA_WIDTH / 2 + PLAYER_RADIUS
            player.velocity[0] = abs(player.velocity[0])
            self.randomize_spike_locations(side="right")

    def handle_possible_floor_collision(self, player):
        floor_y = ARENA_HEIGHT / 2
        if player.pos[1] + PLAYER_RADIUS >= floor_y:
            player.pos[1] = floor_y - PLAYER_RADIUS
            player.velocity[1] = 0
            if not player.is_on_ground:
                player.is_on_ground = True
                self.randomize_spike_locations()

    def move_player(self, player, time_delta):
        if not player.alive:
            player.velocity[0] = 0
            return
        
        if not player.is_on_ground:
            player.velocity[1] += player.gravity * time_delta
            player.pos[1] += player.velocity[1] * time_delta

        if player.pos[1] - PLAYER_RADIUS < -ARENA_HEIGHT / 2:
            player.alive = False

    def process_players_inputs(self, player):
        try:
            while not player.input_queue.empty():
                cmd = player.input_queue.get(block=False)
                if cmd == ClientInputDataFormat.JUMPED:
                    player.velocity[1] = player.jump_force
                    player.is_on_ground = False
        except Empty:
            pass

    def handle_spike_collision(self, player):
        if not player.alive:
            return
        
        px, py = player.pos[0], player.pos[1]
        half_w = ARENA_WIDTH / 2

        if px - PLAYER_RADIUS < -half_w + SPIKES_HEIGHT:
            for _, s_y in self.left_spikes_positions:
                if self._check_single_spike_collision(px, py, -half_w, s_y, is_left=True):
                    player.alive = False
                    return

        elif px + PLAYER_RADIUS > half_w - SPIKES_HEIGHT:
            for _, s_y in self.right_spikes_positions:
                if self._check_single_spike_collision(px, py, half_w, s_y, is_left=False):
                    player.alive = False
                    return

    def _check_single_spike_collision(self, px, py, wall_x, s_y, is_left):
        relative_y = py - s_y
        
        if relative_y < -PLAYER_RADIUS or relative_y > SPIKES_BASE_WIDTH + PLAYER_RADIUS:
            return False

        mid_y = SPIKES_BASE_WIDTH / 2
        dist_from_mid = abs(relative_y - mid_y)
        factor = 1.0 - (dist_from_mid / mid_y)
        factor = max(0.0, factor)

        current_spike_depth = SPIKES_HEIGHT * factor

        if is_left:
            return (px - PLAYER_RADIUS) < (wall_x + current_spike_depth)
        else:
            return (px + PLAYER_RADIUS) > (wall_x - current_spike_depth)

    def _generate_side_slots(self):
        half_h = ARENA_HEIGHT / 2
        num_slots = int(ARENA_HEIGHT / SPIKES_BASE_WIDTH)
        all_slots = [-half_h + SPIKES_BASE_WIDTH * i for i in range(num_slots)]
        random.shuffle(all_slots)

        return all_slots[:SPIKES_NUMBER // 2]

    def randomize_spike_locations(self, side="both"):
        half_w = ARENA_WIDTH / 2
        
        if side in ("left", "both"):
            self.left_spikes_positions = [(half_w, s) for s in self._generate_side_slots()]
            
        if side in ("right", "both"):
            self.right_spikes_positions = [(half_w, s) for s in self._generate_side_slots()]


class ServerPlayerState:

    def __init__(self, id):
        self.level = 1
        self.input_queue: Queue = Queue()
        self.velocity = [200, 0]
        self.pos = [random.randint(-100, 100), 0]
        self.id = id
        self.alive = True
        self.gravity = 1200
        self.jump_force = -600
        self.is_on_ground = False
        self.endGame = False