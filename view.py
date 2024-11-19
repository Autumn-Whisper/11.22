import os
import random
class MainmenuView:
    @staticmethod
    def welcome():
        print("Welcome to Monopoly!")

    @staticmethod
    def choose_if_use_save():
        while True:
            try:
                print("Do you want to use a save file? (y/n)")
                choice = input().strip().lower()
                if choice == 'y':
                    return True
                elif choice == 'n':
                    return False
                else:
                    print("Invalid input, please enter 'y' or 'n'.")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    @staticmethod
    def choose_save_file():
        try:
            print("Please select a save file:")
            saves = os.listdir('save')
            if not saves:
                print("No save files available.")
                return None
            for i, save in enumerate(saves):
                print(f"{i+1}. {save}")
            while True:
                try:
                    i = int(input("Please enter the file number: ")) - 1
                    if 0 <= i < len(saves):
                        file_path = os.path.join('save', saves[i])
                        print(f"You selected {file_path}")
                        return file_path
                    else:
                        print("Out of range, please enter again.")
                except ValueError:
                    print("Invalid input, please enter a number.")
        except FileNotFoundError:
            print("Save directory does not exist.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    @staticmethod
    def choose_new_game_map():
        try:
            print("Please select a game map:")
            maps = os.listdir('map')
            if not maps:
                print("No available map files.")
                return None
            for i, map_file in enumerate(maps):
                print(f"{i+1}. {map_file}")
            while True:
                try:
                    i = int(input("Please enter the map number: ")) - 1
                    if 0 <= i < len(maps):
                        file_path = os.path.join('map', maps[i])
                        print(f"You selected {file_path}")
                        return file_path
                    else:
                        print("Out of range, please enter again.")
                except ValueError:
                    print("Invalid input, please enter a number.")
        except FileNotFoundError:
            print("Map directory does not exist.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    @staticmethod
    def choose_player_num():
        print("Please enter the number of players (2-6):")
        while True:
            try:
                i = int(input())
                if 2 <= i <= 6:
                    print(f"You selected {i} players")
                    return i
                else:
                    print("The number of players must be between 2 and 6, please enter again.")
            except ValueError:
                print("Invalid input, please enter a number.")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    @staticmethod
    def choose_player_name(player_num):
        names = []
        for i in range(player_num):
            while True:
                try:
                    print(f"Please enter the name of player {i+1} (press Enter to use the default name):")
                    name = input().strip()
                    
                    if not name:
                        name = f"Player{i+1}"
                        names.append(name)
                        break
                    
                    if ' ' in name:
                        print("The name cannot contain spaces, please enter again")
                        continue
                    
                    if len(name) > 20:
                        print("The name is too long, please enter a name with 20 characters or less")
                        continue
                        
                    if not name.isascii():
                        print("The name can only contain ASCII characters (English letters, numbers, and punctuation marks)")
                        continue
                        
                    if name in names:
                        print("This name has been used, please choose another name")
                        continue
                        
                    names.append(name)
                    break
                        
                except Exception as e:
                    print(f"An error occurred: {e}, please enter again")
                    
        return names
    
    @staticmethod
    def show_game_start(players):
        print("Game Start! Player List:")
        for player in players.values():
            print(f"{player['name']}: Initial cash ${player['cash']}")

class GameView:
    @staticmethod
    def show_round_start(round_num):
        print(f"\n----------Round {round_num} Start!----------")

    @staticmethod
    def show_round_end(round_num):
        print(f"\n----------Round {round_num} End!----------")

    @staticmethod
    def choose_next_action():
        print("Choose your next action:")
        print("1. Start next round")
        print("2. Save and quit")
        while True:
            try:
                choice = int(input("Please enter the option number: "))
                if choice in [1, 2]:
                    return choice
                else:
                    print("Please enter a valid option number (1 or 2).")
            except ValueError:
                print("Invalid input, please enter a number.")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    @staticmethod
    def is_100_round():
        print("Game Over! Round 100 has been reached!")

    @staticmethod
    def show_player_turn(player_name, money, position, properties, in_jail, jail_turns):
        print(f"\n{player_name}'s turn!")
        print(f"Money: ${money}")
        print(f"Position: Square {position}")
        print(f"Properties owned: {', '.join(properties) if properties else 'None'}")
        if in_jail:
            print(f"In jail for {jail_turns} turns!")

    @staticmethod
    def player_action_menu():
        print("What would you like to do?")
        print("1. Roll dice")
        print("2. View map")
        print("3. View your status")
        print("4. View all players' status")
        print("5. View next player")
        while True:
            try:
                choice = int(input("Please enter the option number: "))
                if choice in [1, 2, 3, 4, 5]:
                    return choice
                else:
                    print("Please enter a valid option number (1-5).")
            except ValueError:
                print("Invalid input, please enter a number.")
            except Exception as e:
                print(f"An error occurred: {e}")
    
    @staticmethod
    def throw_the_dice():
        dice1 = random.randint(1, 4)
        dice2 = random.randint(1, 4)
        print(f"You rolled {dice1} and {dice2}!")
        return dice1, dice2

    @staticmethod
    def reach_a_property(property_name, property_price, property_owner):
        try:
            print(f"You reached {property_name}!")
            if not property_owner:
                print(f"This property is unowned, priced at ${property_price}. Do you want to buy it? (y/n)")
                while True:
                    choice = input().strip().lower()
                    if choice == 'y':
                        return True
                    elif choice == 'n':
                        return False
                    else:
                        print("Invalid input, please enter 'y' or 'n'.")
            else:
                print(f"This property is already owned by {property_owner}! You need to pay rent ${property_price}.")
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    @staticmethod
    def buy_success(property_name):
        try:
            print(f"You successfully bought {property_name}!")
        except Exception as e:
            print(f"An error occurred when showing the purchase success prompt: {e}")

    @staticmethod
    def buy_fail(property_name):
        try:
            print(f"Your funds are insufficient to buy {property_name}!")
        except Exception as e:
            print(f"An error occurred when showing the purchase failure prompt: {e}")

    @staticmethod
    def not_buy_property():
        try:
            print("You chose not to buy this property.")
        except Exception as e:
            print(f"An error occurred when choosing not to buy the property: {e}")

    @staticmethod
    def pay_rent(player_name, owner_name, rent):
        print(f"{player_name} paid rent ${rent} to {owner_name}.")

    @staticmethod
    def reach_own_property(property_name):
        print(f"You reached your property {property_name}.")

    @staticmethod
    def player_bankrupt(player_name):
        print(f"{player_name} is bankrupt! All properties have been confiscated.")

    @staticmethod
    def reach_a_chance():
        print("You reached a chance square!")
        print("Drawing a chance card...")
        amount = random.choice([i * 10 for i in range(-30, 21) if i != 0])
        if amount > 0:
            print(f"Good luck! You received ${amount}!")
        else:
            print(f"Unlucky! You lost ${-amount}!")
        return amount

    @staticmethod
    def reach_a_jail():
        print("You were sent to jail!")

    @staticmethod
    def pass_go():
        print("You passed the starting point and received $1500 salary!")

    @staticmethod
    def pay_income_tax(tax):
        print(f"You need to pay income tax ${tax}.")

    @staticmethod
    def no_effect_square(square_name):
        print(f"You reached {square_name}, nothing happens here.")

    @staticmethod
    def in_jail_options():
        try:
            print("You are in jail, you can choose:")
            print("1. Roll dice to try to get double points out of jail")
            print("2. Pay a $150 fine to get out of jail")
            choice = input("Please enter the option number: ")
            if not choice.isdigit():
                raise ValueError("Please enter a number option")
            choice = int(choice)
            if choice not in [1, 2]:
                raise ValueError("Please enter a valid option number (1 or 2)")
            return choice
        except ValueError as e:
            print(f"Invalid input: {e}")
            return 0
        except Exception as e:
            print(f"An unknown error occurred: {e}")
            return 0

    @staticmethod
    def release_from_jail():
        print("Congratulations! You rolled double points and were immediately released from jail!")

    @staticmethod
    def fail_to_release():
        print("You did not roll double points, so you remain in jail.")

    @staticmethod
    def no_money_to_pay_fine():
        print("Your funds are insufficient to pay the fine, so you cannot get out of jail.")

    @staticmethod
    def invalid_choice():
        print("Invalid choice, please enter again.")

    @staticmethod
    def show_player_states(player):
        print(f"Player {player['name']} status:")
        print(f"Money: ${player['cash']}")
        print(f"Position: Square {player['position']}")
        print(f"Properties: {', '.join(player.get('properties', [])) if player.get('properties') else 'None'}")
        print(f"In jail: {'Yes' if player['in_jail'] else 'No'}")
        if player['in_jail']:
            print(f"In jail for {player['jail_turns']} turns")

    @staticmethod
    def show_all_players_states(players):
        for player in players.values():
            GameView.show_player_states(player)

    @staticmethod
    def show_next_player(player_name):
        print(f"Next player is {player_name}.")

    @staticmethod
    def show_map(squares):
        print("Current map:")
        for pos, square in squares.items():
            print(f"Position {pos}: {square['name']} ({square['square_type']})")

    @staticmethod
    def show_game_over(winners):
        print("\nGame Over!")
        if len(winners) > 1:
            print(f"Draw! Winners: {', '.join(winners)}")
        else:
            print(f"Congratulations {winners[0]}!")
