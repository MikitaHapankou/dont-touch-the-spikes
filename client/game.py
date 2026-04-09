import pygame
from shared.transmitted_data_formats import GameStateBroadcastFormat

class Game:

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.level_font = pygame.font.Font(None, 300)

    @staticmethod
    def return_pygame_events():
        events = pygame.event.get()
        return events

    def update_based_on_server_game_state(self, server_game_state: GameStateBroadcastFormat, client_id):
        self.screen.fill("white")
        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2
        
        pygame.draw.line(self.screen, "black", (center_x - 220, 0), (center_x - 220, 720), 5)
        pygame.draw.line(self.screen, "black", (center_x + 220, 0), (center_x + 220, 720), 5)
        pygame.draw.line(self.screen, "blue", (0, center_y + 234), (1280, center_y + 234), 5)

        if server_game_state.player_positions:
            level_value = int(server_game_state.player_positions[0]["level"])
        else:
            level_value = 1

        level_text_surface = self.level_font.render(str(level_value), True, (220, 220, 220))

        text_rect = level_text_surface.get_rect(center=(center_x, center_y))

        self.screen.blit(level_text_surface, text_rect)

        for player in server_game_state.player_positions:
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
        pygame.display.flip()
