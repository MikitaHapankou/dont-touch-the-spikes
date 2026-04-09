from enum import Enum

class MatchmakingFormingDataFormat(Enum):
    CLIENT_SEEKS_MATCH = 1
    FOUND_MATCH = 2
    PLAYER_ID = 3

class MatchmakingResponse:
    def __init__(self, status, player_id):
        self.status = status
        self.player_id = player_id

class ClientInputDataFormat(Enum):
    JUMPED = 1

class GameStateBroadcastFormat:

    def __init__(self, players_positions, left_spikes_positions, right_spikes_positions):
        self.player_positions = players_positions
        self.left_spikes_positions = left_spikes_positions
        self.right_spikes_positions = right_spikes_positions

class ClientInputData:
    def __init__(self, id):
        self.isJumping = ClientInputDataFormat.JUMPED
        self.id = None
