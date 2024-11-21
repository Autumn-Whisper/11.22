import unittest
from unittest.mock import patch, Mock
from controller import GameController

class TestGameController(unittest.TestCase):

    def setUp(self):
        # set up mock model and mock view
        self.model = Mock()
        self.view = Mock()
        self.controller = GameController(self.model, self.view)

        # Set up basic mock player and game info
        self.player_id = 1
        self.model.players = {
            "1": {
                "name": "Alan",
                "cash": 1000,
                "position": 1,
                "jail_turns": 0,
                "in_jail": True,
                "bankrupt": False,
                "properties": []
            }
        }

        #setup a map size
        self.model.map_size = 114514

    def test_toggle_debug_mode(self):
        # Ensure debug mode starts as False
        self.assertFalse(self.controller.debug_mode)

        # Toggle debug mode to True
        self.controller.toggle_debug_mode()
        self.assertTrue(self.controller.debug_mode)
        self.view.GameView.show_debug_mode_status.assert_called_with(True)

        # Toggle debug mode back to False
        self.controller.toggle_debug_mode()
        self.assertFalse(self.controller.debug_mode)
        self.view.GameView.show_debug_mode_status.assert_called_with(False)

    def test_debug_modify_cash(self):
        self.view.GameView.debug_action_menu.return_value = 1
        self.view.GameView.debug_modify_cash.return_value = 500

        self.controller.handle_debug_actions(self.player_id)

        self.model.update_player_cash.assert_called_once_with("1", 500)

    def test_debug_change_position(self):
        # Mock debug action to change position
        self.view.GameView.debug_action_menu.return_value = 2
        self.view.GameView.debug_choose_position.return_value = 10

        # Configure self.model.squares as a dictionary
        self.model.squares = {
            "10": {
                "square_type": "Property",
                "name": "Park Place",
                "price": 200,
                "owner": None
            }
        }

        # Simulate the behavior of the update_player_position method
        def mock_update_player_position(player_id, new_position):
            self.model.players[player_id]["position"] = new_position

        self.model.update_player_position.side_effect = mock_update_player_position

        # Call the method
        self.controller.handle_debug_actions(self.player_id)

        # Verify model method was called to update the player's position
        self.model.update_player_position.assert_called_once_with("1", 10)

        # Check if the player's position was actually updated
        self.assertEqual(self.model.players["1"]["position"], 10)

    def test_start_game_new(self):
        #set up prerequisite
        self.view.MainmenuView.choose_if_use_save.return_value = False
        self.view.MainmenuView.choose_new_game_map.return_value = "map1"
        self.view.MainmenuView.choose_player_num.return_value = 2
        self.view.MainmenuView.choose_player_name.return_value = ["Alan", "Ben"]

        # test
        self.controller.start_game()

        # expected output
        self.model.setup_new_game.assert_called_once_with("map1", ["Alan", "Ben"])
        self.view.MainmenuView.show_game_start.assert_called_once_with(self.model.players)

    def test_start_game_with_save(self):
        #set up prerequisite
        self.view.MainmenuView.choose_if_use_save.return_value = True
        self.view.MainmenuView.choose_save_file.return_value = "save1"

        # test
        self.controller.start_game()

        # expected output
        self.model.load_game.assert_called_once_with("save1")



    # Handle Square Tests
    def test_handle_square_property_available(self):
        self.model.squares = {
            "1": {
                "square_type": "Property",
                "name": "Park Place",
                "price": 200,
                "owner": None
            }
        }
        # buy property
        self.view.GameView.reach_a_property.return_value = True

        self.controller.handle_square(self.player_id, 1)

        self.assertEqual(self.model.players["1"]["cash"], 800)  # Deduct 200
        self.assertIn("Park Place", self.model.players["1"]["properties"])
        self.view.GameView.buy_success.assert_called_once_with("Park Place")



    def test_handle_square_property_owned_by_other(self):

        self.model.squares = {
            "1": {
                "square_type": "Property",
                "name": "Park Place",
                "rent": 50,
                "owner": "Ben"
            }
        }
        self.model.players["2"] = {"name": "Ben", "cash": 500}

        self.controller.handle_square(self.player_id, 1)

        #cost 50
        self.assertEqual(self.model.players["1"]["cash"], 950)
        # earn 50
        self.assertEqual(self.model.players["2"]["cash"], 550)

        self.view.GameView.pay_rent.assert_called_once_with("Alan", "Ben", 50)



    def test_handle_square_chance(self):
        self.model.squares = {
            "1": {"square_type": "Chance"}
        }

        self.view.GameView.reach_a_chance.return_value = 100

        self.controller.handle_square(self.player_id, 1)

        self.assertEqual(self.model.players["1"]["cash"], 1100)

    def test_handle_square_income_tax(self):
        self.model.squares = {
            "1": {"square_type": "Income Tax"}
        }

        self.controller.handle_square(self.player_id, 1)

        # reduce 10 %
        self.assertEqual(self.model.players["1"]["cash"], 900)
        self.view.GameView.pay_income_tax.assert_called_once_with(100)

    def test_handle_square_go_to_jail(self):
        self.model.squares = {
            "1": {"square_type": "Go to Jail"},
            "10": {"square_type": "In Jail/Just Visiting"}
        }

        # go to jail
        self.controller.handle_square(self.player_id, 1)
        self.assertTrue(self.model.players["1"]["in_jail"])
        # in jail
        self.assertEqual(self.model.players["1"]["position"], 10)
        self.view.GameView.reach_a_jail.assert_called_once()

    def test_handle_square_go(self):
        self.model.squares = {
            "1": {"square_type": "Go"}
        }

        self.controller.handle_square(self.player_id, 1)

        self.assertEqual(self.model.players["1"]["cash"], 2500)
        self.view.GameView.pass_go.assert_called_once()

   # Handle Jail Tests
    @patch.object(GameController, 'handle_dice_throw')
    def test_handle_jail_rolling_doubles(self, mock_handle_dice_throw):
        self.view.GameView.in_jail_options.return_value = 1

        # same point
        self.view.GameView.throw_the_dice.return_value = (3, 3)

        self.controller.handle_jail(self.player_id)

        self.assertFalse(self.model.players["1"]["in_jail"])
        self.assertEqual(self.model.players["1"]["jail_turns"], 0)
        self.view.GameView.release_from_jail.assert_called_once()
        mock_handle_dice_throw.assert_called_once_with(self.player_id)

    def test_handle_jail_fail_to_release(self):
        self.view.GameView.in_jail_options.return_value = 1
        # differernt point
        self.view.GameView.throw_the_dice.return_value = (2, 3)

        self.controller.handle_jail(self.player_id)

        self.assertEqual(self.model.players["1"]["jail_turns"], 1)
        self.view.GameView.fail_to_release.assert_called_once()

    @patch.object(GameController, 'handle_dice_throw')
    def test_handle_jail_pay_fine(self, mock_handle_dice_throw):
        self.view.GameView.in_jail_options.return_value = 2

        self.controller.handle_jail(self.player_id)

        self.assertFalse(self.model.players["1"]["in_jail"])
        # minus 150 as fine
        self.assertEqual(self.model.players["1"]["cash"], 850)
        mock_handle_dice_throw.assert_called_once_with(self.player_id)

    def test_handle_jail_no_money_for_fine(self):
        self.model.players["1"]["cash"] = 100
        self.view.GameView.in_jail_options.return_value = 2

        # no money to pay fine
        self.controller.handle_jail(self.player_id)

        self.view.GameView.no_money_to_pay_fine.assert_called_once()

    def test_handle_jail_invalid_choice(self):
        # Invalid option
        self.view.GameView.in_jail_options.return_value = 3

        self.controller.handle_jail(self.player_id)

        self.view.GameView.invalid_choice.assert_called_once()

    def test_end_game(self):
        self.model.get_winners.return_value = ["Alan", "Ben"]

        self.controller.end_game()

        self.view.GameView.show_game_over.assert_called_once_with(["Alan", "Ben"])

    def player_turn(self, player_id):
        player = self.model.players[str(player_id)]
        self.view.GameView.show_player_turn(
            player['name'], player['cash'], player['position'],
            player.get('properties', []), player['in_jail'], player['jail_turns']
        )

        # Check if the player is bankrupt at the start of their turn
        if player["cash"] < 0:
            self.view.GameView.player_bankrupt(player["name"])
            player["bankrupt"] = True

            # Clear player's properties and reset ownership
            for prop in player.get("properties", []):
                for square in self.model.squares.values():
                    if square["name"] == prop:
                        square["owner"] = ""
            player["properties"] = []
            return  # End the player's turn if bankrupt

        if player['in_jail']:
            self.handle_jail(player_id)
            return

        while True:
            action = self.view.GameView.player_action_menu(self.debug_mode)
            if action == 1:
                self.handle_dice_throw(player_id)
                break
            elif action == 2:
                self.view.GameView.show_map(self.model.squares)
            elif action == 3:
                chosen_player_id = self.view.GameView.choose_player_to_view(self.model.players)
                self.view.GameView.show_player_states(self.model.players[chosen_player_id])
            elif action == 4:
                self.view.GameView.show_all_players_states(self.model.players)
            elif action == 5:
                next_player_id = (player_id % self.model.players_num) + 1
                next_player = self.model.players[str(next_player_id)]
                self.view.GameView.show_next_player(next_player['name'])
            elif action == 6 and self.debug_mode:
                self.handle_debug_actions(player_id)
            else:
                self.view.GameView.invalid_choice()

    def test_player_turn_invalid_choice(self):
        self.view.GameView.player_action_menu.return_value = 99

        self.controller.player_turn(self.player_id)

        self.view.GameView.invalid_choice.assert_called_once()

    def test_handle_dice_throw_move_player(self):
        self.view.GameView.throw_the_dice.return_value = (3, 4)  # Total steps = 7
        self.model.map_size = 10

        # Define squares as a dictionary
        self.model.squares = {
            "8": {
                "square_type": "Property",
                "name": "Test Property",
                "price": 200,
                "owner": None
            }
        }

        # Call the method
        self.controller.handle_dice_throw(self.player_id)

        # Assert the position was updated correctly
        self.model.update_player_position.assert_called_once_with("1", 8)



    @patch.object(GameController, 'handle_dice_throw')
    def test_handle_jail_after_two_turns(self, mock_handle_dice_throw):
        self.model.players["1"]["jail_turns"] = 2
        self.model.players["1"]["cash"] = 200

        self.controller.handle_jail(self.player_id)

        self.assertFalse(self.model.players["1"]["in_jail"])
        # After paying 150
        self.assertEqual(self.model.players["1"]["cash"], 50)
        mock_handle_dice_throw.assert_called_once_with(self.player_id)

    def test_debug_action_no_position_chosen(self):
        self.view.GameView.debug_action_menu.return_value = 2  # Modify position
        self.view.GameView.debug_choose_position.return_value = None  # No position selected

        self.controller.handle_debug_actions(self.player_id)

        self.model.update_player_position.assert_not_called()  # Ensure no update is made



    def test_handle_jail_bankrupt_after_two_turns(self):
        self.model.players["1"]["jail_turns"] = 2
        self.model.players["1"]["cash"] = 100

        self.controller.handle_jail(self.player_id)

        self.assertTrue(self.model.players["1"]["bankrupt"])
        self.view.GameView.player_bankrupt.assert_called_once_with("Alan")

    def test_debug_action_no_action_chosen(self):
        self.view.GameView.debug_action_menu.return_value = None  # No action chosen

        self.controller.handle_debug_actions(self.player_id)

        # Ensure no updates are made
        self.model.update_player_cash.assert_not_called()
        self.model.update_player_position.assert_not_called()

    def test_debug_action_bankruptcy(self):
        self.view.GameView.debug_action_menu.return_value = 1  # Modify cash
        self.view.GameView.debug_modify_cash.return_value = -500  # Negative cash

        # Set up a property owned by the player
        self.model.squares = {"1": {"name": "Test Property", "owner": "Alan"}}
        self.model.players["1"]["properties"] = ["Test Property"]

        # Mock `update_player_cash` to update the player's cash directly
        def mock_update_player_cash(player_id, amount):
            self.model.players[player_id]["cash"] = amount

        self.model.update_player_cash.side_effect = mock_update_player_cash

        # Call the method
        self.controller.handle_debug_actions(self.player_id)

        # Verify the player is marked as bankrupt
        self.assertTrue(self.model.players["1"]["bankrupt"])

        # Verify all properties are cleared
        self.assertEqual(self.model.players["1"]["properties"], [])
        self.assertEqual(self.model.squares["1"]["owner"], "")

        # Verify the `player_bankrupt` view is called
        self.view.GameView.player_bankrupt.assert_called_once_with("Alan")
    def test_end_game_no_winners(self):
        self.model.get_winners.return_value = []  # No winners

        self.controller.end_game()

        # Verify the game over view is called with an empty list
        self.view.GameView.show_game_over.assert_called_once_with([])

    @patch.object(GameController, 'player_turn')
    @patch.object(GameController, 'end_game')
    def test_game_loop(self, mock_end_game, mock_player_turn):
            # Mock game state
            self.model.is_game_over.side_effect = [False, False, False, False, True]
            self.model.round_num = 1
            self.model.players_num = 2
            self.model.players = {"1": {"name": "Alan", "bankrupt": False}, "2": {"name": "Ben", "bankrupt": False}}

            # Mock view and model calls
            self.view.GameView.show_round_start = Mock()
            self.view.GameView.show_round_end = Mock()

            # Call game loop
            self.controller.game_loop()

            # Ensure player_turn is called for each player in every round
            mock_player_turn.assert_any_call(1)
            mock_player_turn.assert_any_call(2)

            # Check round start and end views
            self.view.GameView.show_round_start.assert_called_with(1)
            self.view.GameView.show_round_end.assert_called_with(1)

            # Ensure end_game is called
            mock_end_game.assert_called_once()

    @patch.object(GameController, 'end_game')
    def test_game_loop_game_already_over(self, mock_end_game):
        # Mock `is_game_over` to return True immediately
        self.model.is_game_over.return_value = True

        # Call game loop
        self.controller.game_loop()

        # Ensure end_game is called without any turns
        mock_end_game.assert_called_once()
        self.view.GameView.show_round_start.assert_not_called()
        self.view.GameView.show_round_end.assert_not_called()

    @patch.object(GameController, 'player_turn')
    def test_game_loop_bankrupt_player_skipped(self, mock_player_turn):
        # Mark player 1 as bankrupt
        self.model.players["1"]["bankrupt"] = True
        self.model.players["2"] = {"name": "Ben", "bankrupt": False}

        # Mock the number of players
        self.model.players_num = 2

        # Mock `is_game_over` to end after one round
        self.model.is_game_over.side_effect = [False, False, True]  # Ends after one round

        # Call game loop
        self.controller.game_loop()

        # Ensure `player_turn` is not called for the bankrupt player
        mock_player_turn.assert_called_once_with(2)


    def test_handle_jail_out_of_turns_bankrupt(self):
            self.model.players["1"]["jail_turns"] = 2
            self.model.players["1"]["cash"] = 50  # Not enough to pay fine

            self.controller.handle_jail(self.player_id)

            # Ensure the player is declared bankrupt
            self.assertTrue(self.model.players["1"]["bankrupt"])
            self.view.GameView.player_bankrupt.assert_called_once_with("Alan")
if __name__ == '__main__':
    unittest.main()