import unittest
from map_editor import (
    MapData, GoSquare, PropertySquare, IncomeTaxSquare,
    ChanceSquare, FreeParkingSquare, GoToJailSquare, InJailSquare, Square
)


class TestMapData(unittest.TestCase):
    def setUp(self):
        # Initialize MapData and various square types for reuse in tests
        self.map_data = MapData(10)
        self.go_square = GoSquare()
        self.property_square = PropertySquare("Park Place", 350, 35)
        self.income_tax_square = IncomeTaxSquare()
        self.chance_square = ChanceSquare()
        self.free_parking_square = FreeParkingSquare()
        self.go_to_jail_square = GoToJailSquare()
        self.in_jail_square = InJailSquare()

    def test_add_and_get_square(self):
        # Test adding and retrieving a square
        self.map_data.add_square(1, self.go_square)
        square = self.map_data.get_square(1)
        self.assertIsInstance(square, GoSquare)
        self.assertEqual(square.square_type, "Go")
        self.assertEqual(square.name, "Go")

    def test_edit_square(self):
        # Test editing a square's contents
        self.map_data.add_square(1, self.go_square)
        self.map_data.edit_square(1, self.property_square)
        square = self.map_data.get_square(1)
        self.assertIsInstance(square, PropertySquare)
        self.assertEqual(square.name, "Park Place")
        self.assertEqual(square.price, 350)
        self.assertEqual(square.rent, 35)

    def test_validate_map(self):
        # Test validation on a valid map
        self.map_data.add_square(1, self.go_square)
        self.map_data.add_square(2, self.property_square)
        self.map_data.add_square(3, self.income_tax_square)
        self.map_data.add_square(4, self.chance_square)
        self.map_data.add_square(5, self.free_parking_square)
        self.map_data.add_square(6, self.go_to_jail_square)
        self.map_data.add_square(7, self.in_jail_square)
        errors = self.map_data.validate_map()
        self.assertListEqual(errors, [])

    def test_validate_map_errors(self):
        # Test validation errors in various scenarios

        # No 'Go' square
        self.map_data.add_square(1, self.property_square)
        errors = self.map_data.validate_map()
        self.assertIn("Map must have exactly one 'Go' square, but has 0.", errors)

        # Duplicate 'Go' squares
        self.map_data.add_square(2, self.go_square)
        self.map_data.add_square(3, self.go_square)
        errors = self.map_data.validate_map()
        self.assertIn("Map must have exactly one 'Go' square, but has 2.", errors)

        # 'Go to Jail' square without 'In Jail/Just Visiting'
        self.map_data.add_square(4, self.go_to_jail_square)
        errors = self.map_data.validate_map()
        self.assertIn("Map has a 'Go to Jail' square but no 'In Jail/Just Visiting' square. Please add one.", errors)

        # Duplicate property names
        duplicate_property = PropertySquare("Park Place", 300, 30)
        self.map_data.add_square(5, self.property_square)
        self.map_data.add_square(6, duplicate_property)
        errors = self.map_data.validate_map()
        self.assertIn("Duplicate property names found. Each property must have a unique name.", errors)

    def test_to_dict(self):
        # Test conversion to dictionary
        self.map_data.add_square(1, self.go_square)
        self.map_data.add_square(2, self.property_square)
        map_dict = self.map_data.to_dict()

        # Validate the dictionary structure
        self.assertEqual(map_dict['map_size'], 10)
        self.assertIn('1', map_dict['squares'])
        self.assertIn('2', map_dict['squares'])
        self.assertEqual(map_dict['squares']['1']['square_type'], "Go")
        self.assertEqual(map_dict['squares']['2']['name'], "Park Place")
        self.assertEqual(map_dict['squares']['2']['price'], 350)
        self.assertEqual(map_dict['squares']['2']['rent'], 35)

    def test_from_dict(self):
        # Test reloading map data from dictionary
        data = {
            'map_size': 10,
            'squares': {
                '1': {'square_type': 'Go', 'name': 'Go'},
                '2': {'square_type': 'Property', 'name': 'Park Place', 'price': 350, 'rent': 35, 'owner': None}
            }
        }
        map_data = MapData.from_dict(data)

        # Validate the map data loaded from the dictionary
        self.assertEqual(map_data.map_size, 10)
        self.assertIsInstance(map_data.get_square(1), GoSquare)
        self.assertIsInstance(map_data.get_square(2), PropertySquare)
        self.assertEqual(map_data.get_square(2).name, "Park Place")
        self.assertEqual(map_data.get_square(2).price, 350)
        self.assertEqual(map_data.get_square(2).rent, 35)

    def test_property_square_owner(self):
        # Test setting and retrieving the owner of a PropertySquare
        self.map_data.add_square(2, self.property_square)
        square = self.map_data.get_square(2)
        self.assertIsNone(square.owner)

        # Set owner and verify
        square.owner = "Player 1"
        self.assertEqual(square.owner, "Player 1")

    def test_free_parking_square(self):
        # Test FreeParkingSquare properties
        self.map_data.add_square(3, self.free_parking_square)
        square = self.map_data.get_square(3)
        self.assertIsInstance(square, FreeParkingSquare)
        self.assertEqual(square.square_type, "Free Parking")
        self.assertEqual(square.name, "Free Parking")

    def test_chance_square(self):
        # Test ChanceSquare properties
        self.map_data.add_square(4, self.chance_square)
        square = self.map_data.get_square(4)
        self.assertIsInstance(square, ChanceSquare)
        self.assertEqual(square.square_type, "Chance")
        self.assertEqual(square.name, "Chance")

    def test_go_to_jail_square(self):
        # Test GoToJailSquare properties
        self.map_data.add_square(5, self.go_to_jail_square)
        square = self.map_data.get_square(5)
        self.assertIsInstance(square, GoToJailSquare)
        self.assertEqual(square.square_type, "Go to Jail")
        self.assertEqual(square.name, "Go to Jail")

    def test_in_jail_square(self):
        # Test InJailSquare properties
        self.map_data.add_square(6, self.in_jail_square)
        square = self.map_data.get_square(6)
        self.assertIsInstance(square, InJailSquare)
        self.assertEqual(square.square_type, "In Jail/Just Visiting")
        self.assertEqual(square.name, "In Jail/Just Visiting")

    # Additional tests for edge cases and missing functionality
    def test_edit_undefined_square(self):
        # Test editing a square that does not exist yet
        self.map_data.edit_square(5, self.property_square)
        square = self.map_data.get_square(5)
        self.assertIsInstance(square, PropertySquare)
        self.assertEqual(square.name, "Park Place")

    def test_validate_empty_map(self):
        # Test validation for an empty map
        empty_map_data = MapData(10)
        errors = empty_map_data.validate_map()
        self.assertIn("Map must have exactly one 'Go' square, but has 0.", errors)

    def test_invalid_data_in_from_dict(self):
        # Test invalid data in from_dict
        invalid_data = {
            'map_size': 10,
            'squares': {'1': {'square_type': 'Invalid Type'}}
        }
        map_data = MapData.from_dict(invalid_data)
        square = map_data.get_square(1)
        self.assertIsInstance(square, Square)  # Should fall back to basic Square
        self.assertEqual(square.square_type, "Invalid Type")

    def test_overwrite_square(self):
        # Test adding a square to an already-occupied position
        self.map_data.add_square(1, self.go_square)
        self.map_data.add_square(1, self.property_square)
        square = self.map_data.get_square(1)
        self.assertIsInstance(square, PropertySquare)
        self.assertEqual(square.name, "Park Place")


if __name__ == '__main__':
    unittest.main()