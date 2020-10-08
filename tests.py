import unittest
import main


class test_flapping_scenarios(unittest.TestCase):

    def test_flapping(self):
        expected = [{"service_id": 1210, "amountOfOutages": 2, "sumOfOutages": 20}, {"service_id": 1310, "amountOfOutages": 2, "sumOfOutages": 32}, {"service_id": 1310, "amountOfOutages": 2, "sumOfOutages": 32}]
        got = main.get_flapping_service()
        self.assertEqual(expected, got)


if __name__ == '__main__':
    unittest.main()
