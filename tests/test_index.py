import sys
import unittest

sys.path.insert(0, '/home/dklets/Projects/RentalCars')
from main import rental_cars


class FlaskTestCase(unittest.TestCase):
    # Ensure that app works correctly
    def test_index(self):
        """
        Unit test for app launch

        """
        tester = rental_cars.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
