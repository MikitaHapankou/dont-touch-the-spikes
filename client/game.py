import pygame
from shared.transmitted_data_formats import GameStateBroadcastFormat
from shared.game_constants import *


class Game:

    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.level_font = pygame.font.Font(None, 300)
        self.loss_font = pygame.font.Font(None, 70)
        self.loss_text = self.loss_font.render("Game over!", True, (255, 0, 0))
        self.win_text = self.loss_font.render("You won!", True, (0, 255, 0))
        self.my_player_img_alive_left = pygame.image.load("assets/player1_alive.png").convert_alpha()
        self.enemy_img_alive_left = pygame.image.load("assets/player2_alive_left.png").convert_alpha()
        self.my_player_img_alive_right = pygame.image.load("assets/player1_alive_right.png").convert_alpha()
        self.enemy_img_alive_right = pygame.image.load("assets/player2_alive_right.png").convert_alpha()
        self.my_player_img_dead = pygame.image.load("assets/player1_dead.png").convert_alpha()
        self.enemy_img_dead = pygame.image.load("assets/player2_dead.png").convert_alpha()

        self.last_x_positions = {}
        self.facing_right = {}

    @staticmethod
    def return_pygame_events():
        return pygame.event.get()

    def update_based_on_server_game_state(self, server_game_state: GameStateBroadcastFormat, client_id):
        self.screen.fill("white")
        cx = self.screen.get_width()  / 2
        cy = self.screen.get_height() / 2

        self.draw_arena(cx, cy)

        if server_game_state.player_positions:
            level_value = max(int(p["level"]) for p in server_game_state.player_positions)
        else:
            level_value = 1
        level_surf = self.level_font.render(str(level_value), True, (220, 220, 220))
        self.screen.blit(level_surf, level_surf.get_rect(center=(cx, cy)))

        is_alive = self.draw_players(server_game_state.player_positions, client_id)
        self.draw_spikes(server_game_state.left_spikes_positions,
                         server_game_state.right_spikes_positions, cx, cy)
        pygame.display.flip()

        return is_alive

    def draw_arena(self, cx, cy):
        left_x   = cx - ARENA_WIDTH  / 2
        right_x  = cx + ARENA_WIDTH  / 2
        top_y    = cy - ARENA_HEIGHT / 2
        bottom_y = cy + ARENA_HEIGHT / 2
        wall_w   = 5

        # Left & right walls
        pygame.draw.line(self.screen, "black", (left_x,  0), (left_x,  SCREEN_SIZE[1]), wall_w)
        pygame.draw.line(self.screen, "black", (right_x, 0), (right_x, SCREEN_SIZE[1]), wall_w)
        # Top & bottom floors
        pygame.draw.line(self.screen, "black", (0, top_y),    (SCREEN_SIZE[0], top_y),    wall_w)
        pygame.draw.line(self.screen, "black", (0, bottom_y), (SCREEN_SIZE[0], bottom_y), wall_w)
        floor_rect = pygame.Rect(left_x, bottom_y, ARENA_WIDTH, wall_w + 4)
        pygame.draw.rect(self.screen, (60, 60, 60), floor_rect)

    def draw_players(self, player_positions, client_id):
        cx = self.screen.get_width() / 2
        cy = self.screen.get_height() / 2

        client_died_this_frame = False
        client_won_this_frame = False

        for player in player_positions:
            p_id = player["id"]
            ax, ay = player["pos"]
            is_alive = player["alive"]

            old_x = self.last_x_positions.get(p_id, ax)

            if ax > old_x:
                self.facing_right[p_id] = True  #facing right
            elif ax < old_x:
                self.facing_right[p_id] = False  #facing left

            self.last_x_positions[p_id] = ax

            #facing right by default
            is_facing_right = self.facing_right.get(p_id, True)

            if p_id == client_id:
                #player
                if not is_alive:
                    current_image = self.my_player_img_dead
                    client_died_this_frame = True
                elif is_facing_right:
                    current_image = self.my_player_img_alive_right
                else:
                    current_image = self.my_player_img_alive_left
            else:
                #opponent
                if not is_alive:
                    current_image = self.enemy_img_dead
                elif is_facing_right:
                    current_image = self.enemy_img_alive_right
                else:
                    current_image = self.enemy_img_alive_left

            if is_alive or p_id == client_id:
                sx = cx + ax
                sy = cy + ay
                img_rect = current_image.get_rect(center=(sx, sy))
                self.screen.blit(current_image, img_rect)

            if player["endGame"]:
                client_won_this_frame = True

        if client_died_this_frame:
            self.screen.blit(self.loss_text, self.loss_text.get_rect(center=(cx, cy)))
            return False

        if client_won_this_frame:
            self.screen.blit(self.win_text, self.win_text.get_rect(center=(cx, cy)))
            return False

        return True
    
    def draw_spikes(self, left_spikes, right_spikes, cx, cy):

        for spike in left_spikes:
            wall_ax = -ARENA_WIDTH / 2
            top_ay  = spike[1]
            bot_ay  = top_ay + SPIKES_BASE_WIDTH
            mid_ay  = top_ay + SPIKES_BASE_WIDTH / 2
            tip_ax  = wall_ax + SPIKES_HEIGHT

            pts = [
                (cx + wall_ax, cy + top_ay),
                (cx + wall_ax, cy + bot_ay),
                (cx + tip_ax,  cy + mid_ay),
            ]
            pygame.draw.polygon(self.screen, "red", pts)
            pygame.draw.polygon(self.screen, (180, 0, 0), pts, 2)

        for spike in right_spikes:
            wall_ax = ARENA_WIDTH / 2
            top_ay  = spike[1]
            bot_ay  = top_ay + SPIKES_BASE_WIDTH
            mid_ay  = top_ay + SPIKES_BASE_WIDTH / 2
            tip_ax  = wall_ax - SPIKES_HEIGHT

            pts = [
                (cx + wall_ax, cy + top_ay),
                (cx + wall_ax, cy + bot_ay),
                (cx + tip_ax,  cy + mid_ay),
            ]
            pygame.draw.polygon(self.screen, "red", pts)
            pygame.draw.polygon(self.screen, (180, 0, 0), pts, 2)