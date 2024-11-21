class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.debug_mode = False

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        self.view.GameView.show_debug_mode_status(self.debug_mode)

    def start_game(self):
        self.view.MainmenuView.welcome()
        
        if self.view.MainmenuView.choose_debug_mode():
            self.toggle_debug_mode()
        
        use_save = self.view.MainmenuView.choose_if_use_save()
        
        if use_save:
            save_file = self.view.MainmenuView.choose_save_file()
            self.model.load_game(save_file)
        else:
            map_file = self.view.MainmenuView.choose_new_game_map()
            player_num = self.view.MainmenuView.choose_player_num()
            player_names = self.view.MainmenuView.choose_player_name(player_num)
            self.model.setup_new_game(map_file, player_names)
        
        self.view.MainmenuView.show_game_start(self.model.players)
        self.game_loop()

    def game_loop(self):
        game_saved_and_exited = False
        while not self.model.is_game_over():
            self.view.GameView.show_round_start(self.model.round_num)
            for player_id in range(1, self.model.players_num + 1):
                player = self.model.players[str(player_id)]
                if player['bankrupt']:
                    continue
                self.player_turn(player_id)

                if self.model.is_game_over():
                    break

            if self.model.is_game_over():
                break

            self.view.GameView.show_round_end(self.model.round_num)
            self.model.update_round_num(self.model.round_num + 1)

            if self.model.is_game_over():
                break

            choice = self.view.GameView.choose_next_action()
            if choice == 2:
                self.model.save_game()
                game_saved_and_exited = True
                break

        if not game_saved_and_exited:
            self.end_game()

    def player_turn(self, player_id):
        player = self.model.players[str(player_id)]
        self.view.GameView.show_player_turn(
            player['name'], player['cash'], player['position'],
            player.get('properties', []), player['in_jail'], player['jail_turns']
        )

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
                print("无效的选项，请重新选择。")

    def handle_dice_throw(self, player_id):
        dice1, dice2 = self.view.GameView.throw_the_dice()
        steps = dice1 + dice2
        player = self.model.players[str(player_id)]
        new_position = (player['position'] + steps - 1) % self.model.map_size + 1
        
        if player['position'] + steps > self.model.map_size and new_position != 1:
            player['cash'] += 1500
            self.view.GameView.pass_go()

        self.model.update_player_position(str(player_id), new_position)
        self.handle_square(player_id, new_position)

    def handle_square(self, player_id, position):
        square = self.model.squares[str(position)]
        player = self.model.players[str(player_id)]


        def check_bankruptcy():
            if player['cash'] < 0:
                self.view.GameView.player_bankrupt(player['name'])
                player['bankrupt'] = True

                for prop in player.get('properties', []):
                    for sq in self.model.squares.values():
                        if sq['name'] == prop:
                            sq['owner'] = ''
                player['properties'] = []
                return True
            return False

        if square['square_type'] == 'Property':
            owner = square.get('owner')
            if owner is None or owner == '':
                want_to_buy = self.view.GameView.reach_a_property(
                    square['name'], square['price'], ''
                )
                if want_to_buy:
                    if player['cash'] >= square['price']:
                        player['cash'] -= square['price']
                        square['owner'] = player['name']
                        player.setdefault('properties', []).append(square['name'])
                        self.view.GameView.buy_success(square['name'])
                    else:
                        self.view.GameView.buy_fail(square['name'])
                else:
                    self.view.GameView.not_buy_property()
            else:
                if owner != player['name']:
                    rent = square['rent']
                    player['cash'] -= rent
                    if not check_bankruptcy():
                        for pid, p in self.model.players.items():
                            if p['name'] == owner:
                                p['cash'] += rent
                                break
                        self.view.GameView.pay_rent(player['name'], owner, rent)
                else:
                    self.view.GameView.reach_own_property(square['name'])
        elif square['square_type'] == 'Chance':
            amount = self.view.GameView.reach_a_chance()
            player['cash'] += amount
            check_bankruptcy()
        elif square['square_type'] == 'Income Tax':
            tax = int(player['cash'] * 0.1 // 10 * 10)
            player['cash'] -= tax
            self.view.GameView.pay_income_tax(tax)
            check_bankruptcy()
        elif square['square_type'] == 'Go to Jail':
            jail_position = None
            for pos_str, sq in self.model.squares.items():
                if sq['square_type'] == 'In Jail/Just Visiting':
                    jail_position = int(pos_str)
                    break
            if jail_position is not None:
                player['in_jail'] = True
                player['position'] = jail_position
                self.view.GameView.reach_a_jail()
            else:
                print("未找到监狱方格，无法入狱。")
        elif square['square_type'] == 'Go':
            player['cash'] += 1500
            self.view.GameView.pass_go()
        else:
            self.view.GameView.no_effect_square(square['name'])

    def handle_jail(self, player_id):
        player = self.model.players[str(player_id)]
        if player['jail_turns'] < 2:
            choice = self.view.GameView.in_jail_options()
            if choice == 1:
                dice1, dice2 = self.view.GameView.throw_the_dice()
                if dice1 == dice2:
                    player['in_jail'] = False
                    player['jail_turns'] = 0
                    self.view.GameView.release_from_jail()
                    self.handle_dice_throw(player_id)
                else:
                    player['jail_turns'] += 1
                    self.view.GameView.fail_to_release()
            elif choice == 2:
                if player['cash'] >= 150:
                    player['cash'] -= 150
                    player['in_jail'] = False
                    player['jail_turns'] = 0
                    self.handle_dice_throw(player_id)
                else:
                    self.view.GameView.no_money_to_pay_fine()
            else:
                self.view.GameView.invalid_choice()
        else:
            if player['cash'] >= 150:
                player['cash'] -= 150
                player['in_jail'] = False
                player['jail_turns'] = 0
                self.handle_dice_throw(player_id)
            else:
                self.view.GameView.player_bankrupt(player['name'])
                player['bankrupt'] = True

    def end_game(self):
        winners = self.model.get_winners()
        self.view.GameView.show_game_over(winners)

    def handle_debug_actions(self, player_id):
        action = self.view.GameView.debug_action_menu()
        player = self.model.players[str(player_id)]
        
        if action == 1:
            amount = self.view.GameView.debug_modify_cash()
            self.model.update_player_cash(str(player_id), amount)
            if player['cash'] < 0:
                self.view.GameView.player_bankrupt(player['name'])
                player['bankrupt'] = True
                for prop in player.get('properties', []):
                    for sq in self.model.squares.values():
                        if sq['name'] == prop:
                            sq['owner'] = ''
                player['properties'] = []
            
        elif action == 2:
            position = self.view.GameView.debug_choose_position(self.model.map_size)
            if position:
                self.model.update_player_position(str(player_id), position)
                self.handle_square(player_id, position)
                