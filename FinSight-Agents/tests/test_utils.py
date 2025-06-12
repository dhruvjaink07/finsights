import unittest
from utils.bigquery_helpers import some_helper_function  # Replace with actual function names
from utils.vertexai_helpers import another_helper_function  # Replace with actual function names

class TestUtils(unittest.TestCase):

    def test_some_helper_function(self):
        # Add test logic for some_helper_function
        result = some_helper_function(args)  # Replace with actual arguments
        self.assertEqual(result, expected_result)  # Replace with actual expected result

    def test_another_helper_function(self):
        # Add test logic for another_helper_function
        result = another_helper_function(args)  # Replace with actual arguments
        self.assertEqual(result, expected_result)  # Replace with actual expected result

if __name__ == '__main__':
    unittest.main()