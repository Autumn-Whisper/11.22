from model import GameState
from view import MainmenuView, GameView
from controller import GameController

if __name__ == "__main__":
    model = GameState()
    view = type('View', (), {'MainmenuView': MainmenuView, 'GameView': GameView})
    controller = GameController(model, view)
    controller.start_game() 