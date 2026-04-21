import os
import sys
import types

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Minimal stub modules to allow import-time loading of OCR repository code
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

import unittest
from unittest.mock import patch
from services.ocr_service import pdf_to_text, clean_text


class TestOCRService(unittest.TestCase):

    @patch('services.ocr_service.os.path.exists', return_value=True)
    @patch('services.ocr_service.extract_text_from_images', return_value='hello world')
    @patch('services.ocr_service.pdf_to_images', return_value=['image'])
    def test_pdf_to_text_calls_extraction(self, mock_pdf_to_images, mock_extract_text, mock_exists):
        result = pdf_to_text('dummy.pdf')

        mock_exists.assert_called_once_with('dummy.pdf')
        mock_pdf_to_images.assert_called_once_with('dummy.pdf')
        mock_extract_text.assert_called_once_with(['image'])
        self.assertEqual(result, 'hello world')

    def test_pdf_to_text_raises_when_file_missing(self):
        with self.assertRaises(FileNotFoundError):
            pdf_to_text('missing.pdf')

    def test_clean_text_returns_original_text(self):
        sample = 'This is a test\nLine 2'
        self.assertEqual(clean_text(sample), sample)
