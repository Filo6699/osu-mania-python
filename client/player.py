class Player:
    def __init__(self, uid: int=None, username: str=None) -> None:
        self.id = uid
        self.username = username
        self.game_state = {}
    
    def set_game_state(self, game_state):
        self.game_state = game_state
