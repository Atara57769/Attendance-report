import os
import sys
import types
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if 'services.pdf_generator' not in sys.modules:
    pdf_mod = types.ModuleType('services.pdf_generator')

    class DummyPDFGenerator:
        def __init__(self, output_dir='output'):
            pass

        def create_report_a_pdf(self, model, filename=None):
            return 'dummy.pdf'

        def create_report_b_pdf(self, model, filename=None):
            return 'dummy.pdf'

    pdf_mod.PDFGenerator = DummyPDFGenerator
    sys.modules['services.pdf_generator'] = pdf_mod

from unittest.mock import patch
from processors.processor_a import ProcessorA
from processors.processor_b import ProcessorB


class TestProcessorA(unittest.TestCase):

    def test_parse_returns_report_a_rows(self):
        raw_text = 'ראשון 01/01 09:00 17:00 8.00 טסט'

        processor = ProcessorA()
        report = processor.parse(raw_text)

        self.assertEqual(len(report.rows), 1)
        row = report.rows[0]
        self.assertEqual(row.day, 'ראשון')
        self.assertEqual(row.date, '01/01')
        self.assertEqual(row.entry_time, '09:00')
        self.assertEqual(row.end_time, '17:00')
        self.assertEqual(row.sum, 1.0)
        self.assertIn('ראשון', row.note)
        self.assertIn('טסט', row.note)

    @patch('processors.processor_a.TimeVariationService.apply_variation', return_value=('09:05', '17:05', 8.0))
    def test_apply_variation_updates_model_totals(self, mock_variation):
        raw_text = 'ראשון 01/01 09:00 17:00 8.00 טסט'
        processor = ProcessorA()
        report = processor.parse(raw_text)

        result = processor.apply_variation(report)

        self.assertEqual(result.total_hours, 8.0)
        self.assertEqual(result.total_days, 1)
        self.assertEqual(result.rows[0].entry_time, '09:05')
        self.assertEqual(result.rows[0].end_time, '17:05')

    @patch('processors.processor_a.PDFGenerator.create_report_a_pdf', return_value='report_a.pdf')
    def test_generate_pdf_delegates_to_pdf_generator(self, mock_create_pdf):
        raw_text = 'ראשון 01/01 09:00 17:00 8.00 טסט'
        processor = ProcessorA()
        report = processor.parse(raw_text)

        output = processor.generate_pdf(report, 'output', 'test_report_a')

        mock_create_pdf.assert_called_once()
        self.assertEqual(output, 'report_a.pdf')


class TestProcessorB(unittest.TestCase):

    def test_parse_returns_report_b_rows_and_totals(self):
        raw_text = (
            'ראשון 01/01 09:00 17:00 00:30 8.00 100.00 125.00 150.00 2.00\n'
            '1.00 2.00 3.00 4.00 5.00 08:00'
        )

        processor = ProcessorB()
        report = processor.parse(raw_text)

        self.assertEqual(len(report.rows), 1)
        self.assertEqual(report.total_saturday, 1.0)
        self.assertEqual(report.total_150, 2.0)
        self.assertEqual(report.total_125, 3.0)
        self.assertEqual(report.total_100, 4.0)
        self.assertEqual(report.total_hours, 5.0)

    @patch('processors.processor_b.TimeVariationService.apply_variation', return_value=('09:00', '17:00', 8.0))
    @patch('processors.processor_b.TimeVariationService.apply_break_variation', return_value='00:30')
    @patch('processors.processor_b.TimeVariationService.calculate_hours_with_break', return_value=7.5)
    def test_apply_variation_updates_row_and_totals(self, mock_hours, mock_break, mock_variation):
        raw_text = (
            'ראשון 01/01 09:00 17:00 00:30 8.00 100.00 125.00 150.00 2.00\n'
            '1.00 2.00 3.00 4.00 5.00 08:00'
        )

        processor = ProcessorB()
        report = processor.parse(raw_text)
        report = processor.apply_variation(report)

        self.assertEqual(report.total_hours, 7.5)
        self.assertEqual(report.total_days, 1)
        self.assertEqual(report.rows[0].sum, 7.5)
        self.assertEqual(report.total_100, 15.0)
        self.assertEqual(report.total_125, 18.76)
        self.assertEqual(report.total_150, 0.0)
        self.assertEqual(report.total_saturday, 22.5)

    @patch('processors.processor_b.PDFGenerator.create_report_b_pdf', return_value='report_b.pdf')
    def test_generate_pdf_delegates_to_pdf_generator(self, mock_create_pdf):
        raw_text = 'ראשון 01/01 09:00 17:00 00:30 8.00 100.00 125.00 150.00 2.00\n1.00 2.00 3.00 4.00 5.00 08:00'
        processor = ProcessorB()
        report = processor.parse(raw_text)

        output = processor.generate_pdf(report, 'output', 'test_report_b')

        mock_create_pdf.assert_called_once()
        self.assertEqual(output, 'report_b.pdf')
