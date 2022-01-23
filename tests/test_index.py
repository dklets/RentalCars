from main import rental_cars
import unittest


class FlaskTestCase(unittest.TestCase):
    # Ensure that app works correctly
    def test_index(self):
        tester = rental_cars.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
