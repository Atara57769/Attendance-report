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

# Minimal stub modules for OCR import-time dependencies used by services.attendance_report
if 'fitz' not in sys.modules:
    sys.modules['fitz'] = types.ModuleType('fitz')
if 'PIL' not in sys.modules:
    PIL = types.ModuleType('PIL')
    PIL.__path__ = []
    sys.modules['PIL'] = PIL
if 'PIL.Image' not in sys.modules:
    sys.modules['PIL.Image'] = types.ModuleType('PIL.Image')
if 'cv2' not in sys.modules:
    sys.modules['cv2'] = types.ModuleType('cv2')
if 'numpy' not in sys.modules:
    sys.modules['numpy'] = types.ModuleType('numpy')
if 'pytesseract' not in sys.modules:
    pytesseract = types.ModuleType('pytesseract')
    pytesseract.pytesseract = types.SimpleNamespace(tesseract_cmd='')
    sys.modules['pytesseract'] = pytesseract

from unittest.mock import MagicMock, patch
from services.attendance_report_service import process_attendance_report


class TestAttendanceReport(unittest.TestCase):

    @patch('services.attendance_report.get_processor')
    @patch('services.attendance_report.pdf_to_text', return_value='raw text')
    def test_process_attendance_report_invokes_processor_lifecycle(self, mock_pdf_to_text, mock_get_processor):
        model = object()
        processor = MagicMock()
        processor.parse.return_value = model
        processor.apply_variation.return_value = model
        processor.generate_pdf.return_value = 'output.pdf'
        mock_get_processor.return_value = processor

        result = process_attendance_report('in.pdf', 'out.pdf')

        mock_pdf_to_text.assert_called_once_with('in.pdf')
        mock_get_processor.assert_called_once_with('raw text')
        processor.parse.assert_called_once_with('raw text')
        processor.apply_variation.assert_called_once_with(model)
        processor.generate_pdf.assert_called_once_with(model, 'out.pdf')
        self.assertIs(result, model)
