import pygame
from shared.transmitted_data_formats import GameStateBroadcastFormat
from shared.game_constants import *

class Game:

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.level_font = pygame.font.Font(None, 300)

    @staticmethod
    def return_pygame_events():
        events = pygame.event.get()
        return events

    def update_based_on_server_game_state(self, server_game_state: GameStateBroadcastFormat, client_id):
        self.screen.fill("white")
        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2
        
        self.draw_arena(center_x, center_y)

        if server_game_state.player_positions:
            level_value = int(server_game_state.player_positions[0]["level"])
        else:
            level_value = 1
        level_text_surface = self.level_font.render(str(level_value), True, (220, 220, 220))
        text_rect = level_text_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(level_text_surface, text_rect)

        self.draw_players(server_game_state.player_positions, client_id)
        self.draw_spikes(server_game_state.left_spikes_positions, server_game_state.right_spikes_positions, center_x)
        pygame.display.flip()

    def draw_arena(self, center_x, center_y):
        pygame.draw.line(self.screen, "black", (center_x - ARENA_WIDTH / 2, 0),
                         (center_x - ARENA_WIDTH / 2, SCREEN_SIZE[1]), 5)
        pygame.draw.line(self.screen, "black", (center_x + ARENA_WIDTH / 2, 0),
                         (center_x + ARENA_WIDTH / 2, SCREEN_SIZE[1]), 5)
        pygame.draw.line(self.screen, "black", (0, center_y + ARENA_HEIGHT / 2),
                         (SCREEN_SIZE[0], center_y + ARENA_HEIGHT / 2), 5)
        pygame.draw.line(self.screen, "black", (0, center_y - ARENA_HEIGHT / 2),
                         (SCREEN_SIZE[0], center_y - ARENA_HEIGHT / 2), 5)

    def draw_players(self, player_positions, client_id):
        for player in player_positions:
            p_id = player["id"]
            pos = player["pos"]
            alive = player["alive"]
            if p_id == client_id and alive:
                screen_self_pos = pygame.Vector2(self.screen.get_width() / 2 + pos[0], self.screen.get_height() / 2 + pos[1])
                print(f"Player {client_id} is at x: {pos[0]}, y: {pos[1]}")
                pygame.draw.circle(self.screen, "red", screen_self_pos, 40)
            elif alive:
                screen_enemy_pos = pygame.Vector2(self.screen.get_width() / 2 + pos[0], self.screen.get_height() / 2 + pos[1])
                pygame.draw.circle(self.screen, "blue", screen_enemy_pos, 40)

    def draw_spikes(self, left_spikes, right_spikes, center_x):
        for spike in left_spikes:
            pygame.draw.line(self.screen, "red", (center_x - spike[0], spike[1]), (center_x - spike[0], spike[1] + SPIKES_WIDTH), 10)
        for spike in right_spikes:
            pygame.draw.line(self.screen, "red", (center_x + spike[0], spike[1]), (center_x + spike[0], spike[1] + SPIKES_WIDTH), 10)
