import unittest
import os
import json
from unittest.mock import patch, mock_open
from model import GameState

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
        self.map_data = {
            'map_size': 10,
            'squares': {
                '1': {'square_type': 'Go', 'name': 'Go'},
                '2': {'square_type': 'Property', 'name': 'Park Place', 'price': 350, 'rent': 35, 'owner': None}
            }
        }
        self.player_names = ["Alice", "Bob"]

    @patch("builtins.open", new_callable=mock_open, read_data='{"map_size": 10, "squares": {}}')
    def test_load_game(self, mock_file):
        save_data = {
            'map_size': 10,
            'squares': self.map_data['squares'],
            'players': {
                '1': {'name': 'Alice', 'cash': 1500, 'position': 1, 'in_jail': False, 'jail_turns': 0, 'bankrupt': False, 'properties': []}
            },
            'round_num': 1
        }
        mock_file().read.return_value = json.dumps(save_data)
        self.game_state.load_game('dummy_save_file.save')
        self.assertEqual(self.game_state.map_size, 10)
        self.assertEqual(self.game_state.players_num, 1)
        self.assertEqual(self.game_state.round_num, 1)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_save_game(self, mock_makedirs, mock_file):
        self.game_state.map_size = 10
        self.game_state.squares = self.map_data['squares']
        self.game_state.players = {
            '1': {'name': 'Alice', 'cash': 1500, 'position': 1, 'in_jail': False, 'jail_turns': 0, 'bankrupt': False, 'properties': []}
        }
        self.game_state.round_num = 1
        self.game_state.save_game()

        mock_file.assert_called_with('save/save_round_1.save', 'w')
        handle = mock_file()

        # Retrieve all write calls and concatenate their arguments
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)

        # Compare the deserialized objects
        written_data = json.loads(written_content)
        expected_data = {
            'map_size': 10,
            'squares': self.map_data['squares'],
            'players': self.game_state.players,
            'round_num': 1
        }

        self.assertEqual(written_data, expected_data)

    @patch("builtins.open", new_callable=mock_open, read_data='{"map_size": 10, "squares": {}}')
    def test_setup_new_game(self, mock_file):
        self.game_state.setup_new_game('dummy_map_file.map', self.player_names)
        self.assertEqual(self.game_state.map_size, 10)
        self.assertEqual(self.game_state.players_num, 2)
        self.assertIn('1', self.game_state.players)
        self.assertIn('2', self.game_state.players)

    def test_update_player_position(self):
        self.game_state.players = {'1': {'position': 1}}
        self.game_state.update_player_position('1', 5)
        self.assertEqual(self.game_state.players['1']['position'], 5)

    def test_update_player_cash(self):
        self.game_state.players = {'1': {'cash': 1500}}
        self.game_state.update_player_cash('1', 500)
        self.assertEqual(self.game_state.players['1']['cash'], 2000)

    def test_update_player_in_jail(self):
        self.game_state.players = {'1': {'in_jail': False}}
        self.game_state.update_player_in_jail('1', True)
        self.assertTrue(self.game_state.players['1']['in_jail'])

    def test_update_player_jail_turns(self):
        self.game_state.players = {'1': {'jail_turns': 0}}
        self.game_state.update_player_jail_turns('1', 2)
        self.assertEqual(self.game_state.players['1']['jail_turns'], 2)

    def test_update_round_num(self):
        self.game_state.update_round_num(5)
        self.assertEqual(self.game_state.round_num, 5)

    def test_is_game_over(self):
        self.game_state.players = {
            '1': {'bankrupt': False},
            '2': {'bankrupt': True}
        }
        self.game_state.round_num = 50
        self.assertTrue(self.game_state.is_game_over())

    def test_get_winners(self):
        self.game_state.players = {
            '1': {'name': 'Alice', 'cash': 2000},
            '2': {'name': 'Bob', 'cash': 1500}
        }
        winners = self.game_state.get_winners()
        self.assertEqual(winners, ['Alice'])

if __name__ == '__main__':
    unittest.main()