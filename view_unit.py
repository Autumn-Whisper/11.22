import unittest
from unittest.mock import patch
import os
from view import MainmenuView

class TestMainmenuView(unittest.TestCase):

    @patch('builtins.print')
    def test_welcome(self, mock_print):
        MainmenuView.welcome()
        mock_print.assert_called_once_with("Welcome to Monopoly!")

    @patch('builtins.input', side_effect=['y'])
    def test_choose_if_use_save_yes(self, mock_input):
        result = MainmenuView.choose_if_use_save()
        self.assertTrue(result)

    @patch('builtins.input', side_effect=['n'])
    def test_choose_if_use_save_no(self, mock_input):
        result = MainmenuView.choose_if_use_save()
        self.assertFalse(result)

    @patch('builtins.input', side_effect=['a', 'y'])
    @patch('builtins.print')
    def test_choose_if_use_save_invalid_then_yes(self, mock_print, mock_input):
        result = MainmenuView.choose_if_use_save()
        self.assertTrue(result)
        mock_print.assert_any_call("Invalid input, please enter 'y' or 'n'.")

    @patch('os.listdir', return_value=['save1.save', 'save2.save'])
    @patch('builtins.input', side_effect=['1'])
    @patch('builtins.print')
    def test_choose_save_file_valid(self, mock_print, mock_input, mock_listdir):
        result = MainmenuView.choose_save_file()
        self.assertEqual(result, os.path.join('save', 'save1.save'))

    @patch('os.listdir', return_value=[])
    @patch('builtins.print')
    def test_choose_save_file_no_files(self, mock_print, mock_listdir):
        result = MainmenuView.choose_save_file()
        self.assertIsNone(result)
        mock_print.assert_called_with("No save files available.")

    @patch('os.listdir', side_effect=FileNotFoundError)
    @patch('builtins.print')
    def test_choose_save_file_no_directory(self, mock_print, mock_listdir):
        result = MainmenuView.choose_save_file()
        self.assertIsNone(result)
        mock_print.assert_called_with("Save directory does not exist.")

    @patch('os.listdir', return_value=['map1.map', 'map2.map'])
    @patch('builtins.input', side_effect=['1'])
    @patch('builtins.print')
    def test_choose_new_game_map_valid(self, mock_print, mock_input, mock_listdir):
        result = MainmenuView.choose_new_game_map()
        self.assertEqual(result, os.path.join('map', 'map1.map'))

    @patch('os.listdir', return_value=[])
    @patch('builtins.print')
    def test_choose_new_game_map_no_files(self, mock_print, mock_listdir):
        result = MainmenuView.choose_new_game_map()
        self.assertIsNone(result)
        mock_print.assert_called_with("No available map files.")

    @patch('os.listdir', side_effect=FileNotFoundError)
    @patch('builtins.print')
    def test_choose_new_game_map_no_directory(self, mock_print, mock_listdir):
        result = MainmenuView.choose_new_game_map()
        self.assertIsNone(result)
        mock_print.assert_called_with("Map directory does not exist.")

    @patch('builtins.input', side_effect=['3'])
    def test_choose_player_num_valid(self, mock_input):
        result = MainmenuView.choose_player_num()
        self.assertEqual(result, 3)

    @patch('builtins.input', side_effect=['7', '3'])
    @patch('builtins.print')
    def test_choose_player_num_invalid_then_valid(self, mock_print, mock_input):
        result = MainmenuView.choose_player_num()
        self.assertEqual(result, 3)
        mock_print.assert_any_call("The number of players must be between 2 and 6, please enter again.")

    @patch('builtins.input', side_effect=['Player1', 'Player2'])
    def test_choose_player_name(self, mock_input):
        result = MainmenuView.choose_player_name(2)
        self.assertEqual(result, ['Player1', 'Player2'])

    @patch('builtins.input', side_effect=['Player 1', 'Player2', 'Player1', 'Player2'])
    @patch('builtins.print')
    def test_choose_player_name_invalid_space(self, mock_print, mock_input):
        result = MainmenuView.choose_player_name(2)
        self.assertEqual(result, ['Player2', 'Player1'])
        mock_print.assert_any_call("The name cannot contain spaces, please enter again")

if __name__ == '__main__':
    unittest.main()