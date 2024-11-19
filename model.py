import json
import os

class GameState:
    def __init__(self):
        self.squares = {}
        self.map_size = 0
        self.players = {}
        self.players_num = 0
        self.round_num = 1

    def load_game(self, save_file):
        with open(save_file, 'r') as f:
            data = json.load(f)
            self.map_size = data['map_size']
            self.squares = data['squares']
            self.players = data['players']
            self.players_num = len(self.players)
            self.round_num = data.get('round_num', 1)

    def save_game(self):
        data = {
            'map_size': self.map_size,
            'squares': self.squares,
            'players': self.players,
            'round_num': self.round_num
        }
        if not os.path.exists('save'):
            os.makedirs('save')
        save_file = f"save/save_round_{self.round_num}.save"
        with open(save_file, 'w') as f:
            json.dump(data, f)
        print(f"游戏已保存到 {save_file}")

    def setup_new_game(self, map_file, player_names):
        with open(map_file, 'r') as f:
            data = json.load(f)
            self.map_size = data['map_size']
            self.squares = data['squares']
        self.players_num = len(player_names)
        self.players = {}
        for i, name in enumerate(player_names, 1):
            self.players[str(i)] = {
                'name': name if name else f"玩家{i}",
                'cash': 1500,
                'position': 1,
                'in_jail': False,
                'jail_turns': 0,
                'bankrupt': False,
                'properties': []
            }

    def update_player_position(self, player_id, new_position):
        self.players[player_id]['position'] = new_position

    def update_player_cash(self, player_id, amount):
        self.players[player_id]['cash'] += amount

    def update_player_in_jail(self, player_id, in_jail):
        self.players[player_id]['in_jail'] = in_jail

    def update_player_jail_turns(self, player_id, turns):
        self.players[player_id]['jail_turns'] = turns

    def update_round_num(self, new_round_num):
        self.round_num = new_round_num

    def is_game_over(self):
        active_players = [p for p in self.players.values() if not p['bankrupt']]
        return len(active_players) <= 1 or self.round_num > 100

    def get_winners(self):
        max_cash = max([p['cash'] for p in self.players.values()])
        winners = [p['name'] for p in self.players.values() if p['cash'] == max_cash]
        return winners