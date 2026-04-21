import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from unittest.mock import patch
from services.time_variation_service import TimeVariationService


class TestTimeVariationService(unittest.TestCase):

    def test_calculate_hours_returns_correct_value(self):
        self.assertEqual(TimeVariationService.calculate_hours('09:00', '17:00'), 8.0)

    def test_calculate_hours_invalid_times_returns_zero(self):
        self.assertEqual(TimeVariationService.calculate_hours('17:00', '09:00'), 0.0)
        self.assertEqual(TimeVariationService.calculate_hours('bad', '17:00'), 0.0)

    @patch('services.time_variation_service.random.randint', side_effect=[5, 10])
    def test_apply_variation_adds_random_minutes(self, mock_randint):
        entry, exit, hours = TimeVariationService.apply_variation('09:00', '17:00')
        self.assertEqual(entry, '09:05')
        self.assertEqual(exit, '17:10')
        self.assertAlmostEqual(hours, 8.08, places=2)

    @patch('services.time_variation_service.random.randint', return_value=7)
    def test_apply_break_variation_adds_minutes(self, mock_randint):
        result = TimeVariationService.apply_break_variation('00:30')
        self.assertEqual(result, '00:37')

    def test_calculate_hours_with_break_subtracts_break(self):
        hours = TimeVariationService.calculate_hours_with_break('09:00', '17:00', '00:30')
        self.assertEqual(hours, 7.5)

    def test_calculate_total_hours_and_days_from_rows(self):
        class DummyRow:
            def __init__(self, date, sum_value):
                self.date = date
                self.sum = sum_value

        rows = [DummyRow('01/01', 8.0), DummyRow('01/01', 0.0), DummyRow('02/01', 7.0)]
        self.assertEqual(TimeVariationService.calculate_total_hours(rows), 15.0)
        self.assertEqual(TimeVariationService.calculate_total_days(rows), 2)
