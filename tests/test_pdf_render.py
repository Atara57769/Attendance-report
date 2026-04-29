from datetime import time
from pathlib import Path

import pytest

from core.exceptions import PDFGenerationError
from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from pdf_render.base_render import BasePDFService
from pdf_render.render_a import PDFServiceA
from pdf_render.render_b import PDFServiceB


class DummyPDFService(BasePDFService):
    def _summary(self, report):
        return "summary"

    def _table(self, report):
        return "table"

    def _conclusion(self, report):
        return "conclusion"

    def _build_filename(self):
        return "dummy"


TEST_OUTPUT_DIR = Path("tests_output")


def test_base_pdf_generate_and_elements(monkeypatch):
    service = DummyPDFService(output_dir=str(TEST_OUTPUT_DIR))
    monkeypatch.setattr(service, "_build_pdf", lambda elements, filename: f"{filename}:{len(elements)}")
    result = service.generate(AttendanceReport(rows=[]))
    assert result == "dummy:8"


def test_base_pdf_generate_wraps_errors():
    service = DummyPDFService(output_dir=str(TEST_OUTPUT_DIR))
    service._build_filename = lambda: (_ for _ in ()).throw(RuntimeError("bad filename"))
    with pytest.raises(PDFGenerationError, match="Failed to generate PDF: bad filename"):
        service.generate(AttendanceReport(rows=[]))


def test_build_elements_wraps_errors():
    service = DummyPDFService(output_dir=str(TEST_OUTPUT_DIR))
    service._summary = lambda report: (_ for _ in ()).throw(RuntimeError("bad summary"))
    with pytest.raises(PDFGenerationError, match="Failed to build PDF elements: bad summary"):
        service._build_elements(AttendanceReport(rows=[]))


def test_build_pdf_happy_path_and_failure(monkeypatch):
    service = DummyPDFService(output_dir=str(TEST_OUTPUT_DIR))

    class FakeDoc:
        def __init__(self, path, **kwargs):
            self.path = path

        def build(self, elements):
            self.elements = elements

    monkeypatch.setattr("pdf_render.base_render.SimpleDocTemplate", FakeDoc)
    path = service._build_pdf(["a"], "file")
    assert path.endswith("file.pdf")

    class FailingDoc(FakeDoc):
        def build(self, elements):
            raise RuntimeError("doc failed")

    monkeypatch.setattr("pdf_render.base_render.SimpleDocTemplate", FailingDoc)
    with pytest.raises(PDFGenerationError, match="Failed to build PDF file: doc failed"):
        service._build_pdf(["a"], "file")


def test_title_subtitle_and_table_style():
    service = DummyPDFService(output_dir=str(TEST_OUTPUT_DIR))
    assert service._title().text == "Attendance Report"
    assert "Generated on" in service._subtitle().text
    assert service._table_style() is not None


def test_pdf_service_a_helpers():
    report = AttendanceReport(
        rows=[AttendanceRow(day="Sun", entry_time=time(8, 0), end_time=time(16, 0), sum=8.0, note="ok")],
        total_hours=8.0,
        total_days=1,
        hour_payment=10.0,
        total_payment=80.0,
    )
    service = PDFServiceA(output_dir="tests_output")
    assert service._build_filename().startswith("report_a_")
    assert service._summary(report) is not None
    assert service._table(report) is not None
    assert "Conclusion" in service._conclusion(report).text


def test_pdf_service_b_helpers():
    report = AttendanceReport(
        rows=[AttendanceRow(day="Sun", entry_time=time(8, 0), end_time=time(16, 0), break_time=time(0, 15), sum=8.0)],
        total_hours=8.0,
        total_days=1,
        total_100=7.0,
        total_125=1.0,
        total_150=0.0,
        total_saturday=0.0,
    )
    service = PDFServiceB(output_dir="tests_output")
    assert service._build_filename().startswith("report_b_")
    assert service._summary(report) is not None
    assert service._table(report) is not None
    assert "Conclusion" in service._conclusion(report).text
