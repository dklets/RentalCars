from main import rental_cars
import unittest
import re


class FlaskTestCase(unittest.TestCase):
    # Tests cars list
    def test_cars(self):
        tester = rental_cars.test_client(self)
        response = tester.get('/cars-list')
        symbols = re.findall(r'(?<=<td>).*?(?=</td>)', str(response.data))
        i = 0
        while i < len(symbols):
            if len(symbols[i]) > 30:
                del symbols[i]
            i += 1
        self.assertEqual(len(symbols), 30)


if __name__ == '__main__':
    unittest.main()
