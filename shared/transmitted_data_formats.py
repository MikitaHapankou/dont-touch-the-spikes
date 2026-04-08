from enum import Enum
# sending whole python objects seems slow, but is enough for our needs (alternative - JSON)
# at least IDE helps you when you write messages which will be transmitted

class MatchmakingFormingDataFormat(Enum): # clients' requests and server responses share the same format
    CLIENT_SEEKS_MATCH = 1
    FOUND_MATCH = 2


class ClientInputDataFormat(Enum):
    CHANGED_DIRECTION = 1


class GameStateBroadcastFormat:  # later this exchange format will look different

    def __init__(self, players_positions):
        self.player_positions = players_positions