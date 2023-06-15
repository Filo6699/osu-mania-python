class Game:
    def __init__(self) -> None:
        self.players = []
        self.slots = {
            "1": {},
            "2": {},
            "3": {},
            "4": {},
            "5": {}
        }
        self.game_is_running = False
        self.chat_msgs = []
    
    def add_player(self, user):
        for ind, slot in self.slots.items():
            if slot:
                continue
            self.slots[ind] = {"username": user.username, "play_count": user.play_count}
            break
        else:
            print("[LOBBY] Too many players")
    
    def remove_player(self, user):
        for ind, slot in self.slots.items():
            if slot and slot['username'] == user.username:
                self.slots[ind] = {}
                break
