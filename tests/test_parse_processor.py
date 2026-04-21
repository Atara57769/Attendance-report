import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from processores.parse_processor import AttendanceParsingService


class TestParseProcessor(unittest.TestCase):

    def setUp(self):
        self.svc = AttendanceParsingService()

    def test_normalize_line_replaces_pipes_and_collapses_spaces(self):
        value = self.svc.normalize_line('A | B   C')
        self.assertEqual(value, 'A B C')

    def test_extract_times_parses_text_with_colons_and_numbers(self):
        times = self.svc.extract_times('09:00 1700 14.30 823')
        self.assertEqual(times, ['09:00', '17:00', '14:30', '08:23'])

    def test_extract_numbers_converts_hundreds_to_decimal(self):
        numbers = self.svc.extract_numbers('100 12.50 35')
        self.assertEqual(numbers, [1.0, 12.5, 35.0])

    def test_extract_day_and_date(self):
        self.assertEqual(self.svc.extract_day('יום ראשון 01/01'), 'ראשון')
        self.assertEqual(self.svc.extract_date('תאריך 3-12-2024'), '3-12-2024')

    def test_clean_text_removes_numbers_and_special_chars(self):
        value = self.svc.clean_text('09:00 יום ראשון 01/01 תשלום!')
        self.assertEqual(value, 'יום ראשון  תשלום')

    def test_extract_totals_from_full_text(self):
        self.assertEqual(self.svc.extract_total_hours('12.50 שעות'), 12.5)
        self.assertEqual(self.svc.extract_total_days('3 ימים'), 3)
        self.assertEqual(self.svc.extract_hour_payment('35.20 תשלום לשעה'), 35.2)
        self.assertEqual(self.svc.extract_total_payment('450.00 תשלום'), 450.0)
