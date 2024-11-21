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

    @patch.object(GameController, 'handle_dice_throw')
    def test_handle_jail_after_two_turns(self, mock_handle_dice_throw):
        self.model.players["1"]["jail_turns"] = 2
        self.model.players["1"]["cash"] = 200

        self.controller.handle_jail(self.player_id)

        self.assertFalse(self.model.players["1"]["in_jail"])
        # After paying 150
        self.assertEqual(self.model.players["1"]["cash"], 50)
        mock_handle_dice_throw.assert_called_once_with(self.player_id)

    def test_handle_jail_bankrupt_after_two_turns(self):
        self.model.players["1"]["jail_turns"] = 2
        self.model.players["1"]["cash"] = 100

        self.controller.handle_jail(self.player_id)

        self.assertTrue(self.model.players["1"]["bankrupt"])
        self.view.GameView.player_bankrupt.assert_called_once_with("Alan")



if __name__ == '__main__':
    unittest.main()