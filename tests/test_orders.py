import sys
import unittest
import re

sys.path.insert(0, '/home/dklets/Projects/RentalCars')
from main import rental_cars


class FlaskTestCase(unittest.TestCase):
    # Tests orders list
    def test_orders(self):
        """
        Unit test for orders_list

        """
        tester = rental_cars.test_client(self)
        response = tester.get('/orders-list')

        symbols = re.findall(r'(?<=<td>).*?(?=</td>)', str(response.data))
        i = 0
        while i < len(symbols):
            if len(symbols[i]) > 30:
                del symbols[i]
            i += 1
        self.assertEqual(len(symbols), 90)


if __name__ == '__main__':
    unittest.main()
