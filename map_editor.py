import json
import os

# Model 部分

class Square:
    def __init__(self, square_type, name=None):
        self.square_type = square_type
        self.name = name

class GoSquare(Square):
    def __init__(self):
        super().__init__('Go', 'Go')

class PropertySquare(Square):
    def __init__(self, name, price, rent):
        super().__init__('Property', name)
        self.price = price
        self.rent = rent
        self.owner = None

class IncomeTaxSquare(Square):
    def __init__(self):
        super().__init__('Income Tax', 'Income Tax')

class ChanceSquare(Square):
    def __init__(self):
        super().__init__('Chance', 'Chance')

class FreeParkingSquare(Square):
    def __init__(self):
        super().__init__('Free Parking', 'Free Parking')

class GoToJailSquare(Square):
    def __init__(self):
        super().__init__('Go to Jail', 'Go to Jail')

class InJailSquare(Square):
    def __init__(self):
        super().__init__('In Jail/Just Visiting', 'In Jail/Just Visiting')

class MapData:
    def __init__(self, map_size):
        self.map_size = map_size
        self.squares = {}

    def add_square(self, position, square):
        self.squares[position] = square

    def edit_square(self, position, square):
        self.squares[position] = square

    def get_square(self, position):
        return self.squares.get(position)

    def validate_map(self):
        errors = []
        go_count = sum(1 for sq in self.squares.values() if sq.square_type == 'Go')
        in_jail_count = sum(1 for sq in self.squares.values() if sq.square_type == 'In Jail/Just Visiting')
        go_to_jail_exists = any(sq.square_type == 'Go to Jail' for sq in self.squares.values())

        if go_count != 1:
            errors.append(f"Map must have exactly one 'Go' square, but has {go_count}.")
        if in_jail_count > 1:
            errors.append(f"Map can only have one 'In Jail/Just Visiting' square, but has {in_jail_count}.")
        if go_to_jail_exists and in_jail_count == 0:
            errors.append(f"Map has a 'Go to Jail' square but no 'In Jail/Just Visiting' square. Please add one.")
        property_names = [sq.name for sq in self.squares.values() if sq.square_type == 'Property']
        if len(property_names) != len(set(property_names)):
            errors.append("Duplicate property names found. Each property must have a unique name.")
        return errors

    def to_dict(self):
        squares_dict = {}
        for pos, square in self.squares.items():
            square_data = {
                'square_type': square.square_type,
                'name': square.name
            }
            if isinstance(square, PropertySquare):
                square_data['price'] = square.price
                square_data['rent'] = square.rent
                square_data['owner'] = square.owner
            squares_dict[str(pos)] = square_data
        return {
            'map_size': self.map_size,
            'squares': squares_dict
        }

    @staticmethod
    def from_dict(data):
        map_data = MapData(data['map_size'])
        squares_data = data['squares']
        for pos_str, sq_data in squares_data.items():
            pos = int(pos_str)
            square_type = sq_data['square_type']
            name = sq_data.get('name')
            if square_type == 'Go':
                square = GoSquare()
            elif square_type == 'Property':
                price = sq_data.get('price')
                rent = sq_data.get('rent')
                square = PropertySquare(name, price, rent)
                square.owner = sq_data.get('owner')
            elif square_type == 'Income Tax':
                square = IncomeTaxSquare()
            elif square_type == 'Chance':
                square = ChanceSquare()
            elif square_type == 'Free Parking':
                square = FreeParkingSquare()
            elif square_type == 'Go to Jail':
                square = GoToJailSquare()
            elif square_type == 'In Jail/Just Visiting':
                square = InJailSquare()
            else:
                square = Square(square_type, name)
            map_data.add_square(pos, square)
        return map_data

# View 部分

def prompt(message):
    return input(message)

def display(message):
    print(message)

def display_options(options):
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")

def display_map_summary(map_data):
    display("Map Summary:")
    for pos in range(1, map_data.map_size+1):
        sq = map_data.get_square(pos)
        if sq:
            stype = sq.square_type
            name = sq.name
            if stype == "Property":
                display(f"Square {pos}: {stype}, {name} (Price: {sq.price}, Rent: {sq.rent})")
            else:
                display(f"Square {pos}: {stype}, {name}")
        else:
            display(f"Square {pos}: Undefined")

def display_errors(errors):
    for error in errors:
        display(error)

# Controller 部分

def create_new_map():
    display("Creating a new map.")
    while True:
        size_input = prompt("Enter map size (number of squares, minimum 8): ")
        try:
            size = int(size_input)
            if size >= 8:
                break
            else:
                display("Map size must be at least 8.")
        except ValueError:
            display("Invalid input, please enter an integer.")
    map_data = MapData(size)
    display("Now, define each square.")
    for pos in range(1, size+1):
        display(f"Define square {pos}:")
        square = define_square(pos, map_data)
        map_data.add_square(pos, square)
    errors = map_data.validate_map()
    if errors:
        display("Map validation error:")
        display_errors(errors)
    else:
        display("Map validation passed.")
    return map_data

def define_square(pos, map_data):
    square_types = ["Go", "Property", "Income Tax", "Chance", "Free Parking", "Go to Jail", "In Jail/Just Visiting"]
    while True:
        display(f"Select type for square {pos}:")
        display_options(square_types)
        choice_input = prompt("Enter the number corresponding to the square type: ")
        try:
            choice = int(choice_input)
            if 1 <= choice <= len(square_types):
                selected_type = square_types[choice-1]
                square = None
                if selected_type == "Go":
                    go_count = sum(1 for sq in map_data.squares.values() if sq.square_type == 'Go')
                    if go_count >= 1:
                        display("Already exists a 'Go' square, cannot have multiple 'Go' squares.")
                        continue
                    square = GoSquare()
                elif selected_type == "Property":
                    name = ''
                    while not name:
                        name = prompt("Enter property name: ").strip()
                        if name == '':
                            display("Property name cannot be empty.")
                    property_names = [sq.name for sq in map_data.squares.values() if sq.square_type == 'Property']
                    if name in property_names:
                        display("Duplicate property name found. Please use a different name.")
                        continue
                    while True:
                        price_input = prompt("Enter property price (integer): ")
                        try:
                            price = int(price_input)
                            if price < 0:
                                display("Price cannot be negative.")
                                continue
                            break
                        except ValueError:
                            display("Invalid price, please enter an integer.")
                    while True:
                        rent_input = prompt("Enter property rent (integer): ")
                        try:
                            rent = int(rent_input)
                            if rent < 0:
                                display("Rent cannot be negative.")
                                continue
                            break
                        except ValueError:
                            display("Invalid rent, please enter an integer.")
                    square = PropertySquare(name, price, rent)
                elif selected_type == "Income Tax":
                    square = IncomeTaxSquare()
                elif selected_type == "Chance":
                    square = ChanceSquare()
                elif selected_type == "Free Parking":
                    square = FreeParkingSquare()
                elif selected_type == "Go to Jail":
                    square = GoToJailSquare()
                elif selected_type == "In Jail/Just Visiting":
                    in_jail_count = sum(1 for sq in map_data.squares.values() if sq.square_type == 'In Jail/Just Visiting')
                    if in_jail_count >= 1:
                        display("Already exists an 'In Jail/Just Visiting' square, cannot have multiple.")
                        continue
                    square = InJailSquare()
                else:
                    display("Invalid square type selected.")
                    continue
                return square
            else:
                display(f"Invalid choice, please enter a number between 1 and {len(square_types)}.")
        except ValueError:
            display("Invalid input, please enter a number.")

def edit_map(map_data):
    display("Starting map edit.")
    while True:
        display("Please select an option:")
        options = ["Edit a square", "Show map summary", "Finish editing"]
        display_options(options)
        choice = prompt("Enter your choice: ")
        if choice == '1':
            while True:
                pos_input = prompt(f"Enter the number of the square to edit (1-{map_data.map_size}): ")
                try:
                    pos = int(pos_input)
                    if 1 <= pos <= map_data.map_size:
                        display(f"Editing square {pos}")
                        square = define_square(pos, map_data)
                        map_data.edit_square(pos, square)
                        break
                    else:
                        display(f"Invalid square number, please enter a number between 1 and {map_data.map_size}.")
                except ValueError:
                    display("Invalid input, please enter a square number.")
            errors = map_data.validate_map()
            if errors:
                display("Map validation error:")
                display_errors(errors)
            else:
                display("Map validation passed.")
        elif choice == '2':
            display_map_summary(map_data)
        elif choice == '3':
            break
        else:
            display("Invalid choice, please enter 1, 2, or 3.")

def save_map(map_data, map_file):
    display(f"Saving map to {map_file}")
    map_data_dict = map_data.to_dict()
    try:
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(map_data_dict, f, indent=4, ensure_ascii=False)
        display("Map saved successfully.")
    except Exception as e:
        display(f"Failed to save map: {e}")

def load_map(map_file):
    display(f"Loading map from {map_file}")
    try:
        with open(map_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            map_data = MapData.from_dict(data)
            display(f"Map loaded successfully. Map size: {map_data.map_size} squares.")
            return map_data
    except FileNotFoundError:
        display(f"Map file {map_file} not found.")
        return None
    except json.JSONDecodeError:
        display(f"Error parsing {map_file}. Is it a valid map file?")
        return None
    except Exception as e:
        display(f"An error occurred: {e}")
        return None

def main_menu():
    display("Welcome to Monopoly Map Editor.")
    while True:
        display("Please select an option:")
        options = ["Create a new map", "Load an existing map", "Exit"]
        display_options(options)
        choice = prompt("Enter your choice: ")
        if choice == '1':
            map_data = create_new_map()
            while True:
                display("Would you like to edit the map?")
                edit_options = ["Yes", "No"]
                display_options(edit_options)
                edit_choice = prompt("Enter your choice: ")
                if edit_choice == '1':
                    edit_map(map_data)
                    break
                elif edit_choice == '2':
                    break
                else:
                    display("Invalid choice.")
            while True:
                errors = map_data.validate_map()
                if not errors:
                    while True:
                        map_file = prompt("Enter the name of the map file to save (e.g., 'custom.map'): ").strip()
                        if map_file:
                            save_map(map_data, map_file)
                            break
                        else:
                            display("File name cannot be empty.")
                    break  
                else:
                    display("Map has validation errors:")
                    display_errors(errors)
                    fix_options = ["Continue editing", "Discard changes"]
                    display_options(fix_options)
                    fix_choice = prompt("Select: ")
                    if fix_choice == '1':
                        edit_map(map_data)
                    else:
                        display("Discarding changes.")
                        break
        elif choice == '2':
            while True:
                map_file = prompt("Enter the name of the map file to load: ").strip()
                if os.path.exists(map_file):
                    map_data = load_map(map_file)
                    if map_data:
                        break
                else:
                    display(f"File {map_file} does not exist.")
            if map_data:
                edit_map(map_data)
                while True:
                    errors = map_data.validate_map()
                    if not errors:
                        while True:
                            map_file = prompt("Enter the name of the map file to save (e.g., 'custom.map'): ").strip()
                            if map_file:
                                save_map(map_data, map_file)
                                break
                            else:
                                display("File name cannot be empty.")
                        break
                    else:
                        display("Map has validation errors:")
                        display_errors(errors)
                        fix_options = ["Continue editing", "Discard changes"]
                        display_options(fix_options)
                        fix_choice = prompt("Select: ")
                        if fix_choice == '1':
                            edit_map(map_data)
                        else:
                            display("Discarding changes.")
                            break
        elif choice == '3':
            display("Exiting map editor.")
            break
        else:
            display("Invalid choice.")

if __name__ == "__main__":
    main_menu()