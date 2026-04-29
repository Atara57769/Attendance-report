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

from factory.processor_factory import get_processor
from processors.processor_a import ProcessorA
from processors.processor_b import ProcessorB


class TestProcessorFactory(unittest.TestCase):

    def test_get_processor_returns_processor_a_for_a_keywords(self):
        processor = get_processor('מחיר לשעה זה טקסט')
        self.assertIsInstance(processor, ProcessorA)

    def test_get_processor_returns_processor_b_for_b_keywords(self):
        processor = get_processor('הנשר הפסקה 150')
        self.assertIsInstance(processor, ProcessorB)

    def test_get_processor_returns_processor_b_for_fallback_150(self):
        processor = get_processor('מסמך עם 150 מספר')
        self.assertIsInstance(processor, ProcessorB)

    def test_get_processor_returns_processor_a_when_unknown(self):
        processor = get_processor('אין נתונים מתאימים כאן')
        self.assertIsInstance(processor, ProcessorA)
