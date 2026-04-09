import pygame
from shared.transmitted_data_formats import GameStateBroadcastFormat

class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))

    @staticmethod
    def return_pygame_events():
        events = pygame.event.get()
        return events

    def update_based_on_server_game_state(self, server_game_state: GameStateBroadcastFormat, id):
        self.screen.fill("white")
        for player in server_game_state.player_positions:
            p_id = player["id"]
            pos = player["pos"]
            if p_id == id:
                screen_self_pos = pygame.Vector2(self.screen.get_width() / 2 + pos[0], self.screen.get_height() / 2 + pos[1])
                print(f"Player {id} is at x: {pos[0]}, y: {pos[1]}")
                pygame.draw.circle(self.screen, "red", screen_self_pos, 40)
            else:
                screen_enemy_pos = pygame.Vector2(self.screen.get_width() / 2 + pos[0], self.screen.get_height() / 2 + pos[1])
                pygame.draw.circle(self.screen, "blue", screen_enemy_pos, 40)
        pygame.display.flip()
