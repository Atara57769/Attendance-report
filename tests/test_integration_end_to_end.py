from pathlib import Path

from factory import processor_factory as factory_module
from factory.processor_factory import ProcessorFactory
from parse.base_parser import BaseParsingService
from pdf_render.render_a import PDFServiceA
from pdf_render.render_b import PDFServiceB
from services.attendance_report_service import AttendanceReportService


INTEGRATION_OUTPUT_DIR = Path("tests_output/integration")


class FixedPDFServiceA(PDFServiceA):
    def __init__(self):
        super().__init__(output_dir=str(INTEGRATION_OUTPUT_DIR))

    def _build_filename(self) -> str:
        return "integration_report_a"


class FixedPDFServiceB(PDFServiceB):
    def __init__(self):
        super().__init__(output_dir=str(INTEGRATION_OUTPUT_DIR))

    def _build_filename(self) -> str:
        return "integration_report_b"


def _extract_english_day(line: str):
    for day in ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"):
        if day in line:
            return day
    return None


def test_process_report_a_end_to_end_with_fake_ocr(monkeypatch):
    monkeypatch.setattr(BaseParsingService, "extract_day", staticmethod(_extract_english_day))
    monkeypatch.setattr(factory_module, "PDFServiceA", FixedPDFServiceA)

    pdf_path = INTEGRATION_OUTPUT_DIR / "integration_report_a.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    raw_text = "\n".join(
        [
            "Sunday 08:00 17:00 8.50 Main Office",
            "summary footer without overtime markers",
        ]
    )

    service = AttendanceReportService(
        factory=ProcessorFactory(),
        ocr_service=lambda path: raw_text,
    )

    report = service.process("fake-a.pdf")

    assert len(report.rows) == 1
    assert report.rows[0].day == "Sunday"
    assert report.rows[0].entry_time is not None
    assert report.rows[0].end_time is not None
    assert report.total_days == 1
    assert pdf_path.exists()


def test_process_report_b_end_to_end_with_fake_ocr(monkeypatch):
    monkeypatch.setattr(BaseParsingService, "extract_day", staticmethod(_extract_english_day))
    monkeypatch.setattr(factory_module, "PDFServiceB", FixedPDFServiceB)

    pdf_path = INTEGRATION_OUTPUT_DIR / "integration_report_b.pdf"
    if pdf_path.exists():
        pdf_path.unlink()

    raw_text = "\n".join(
        [
            "Monday 08:00 17:00 00:15 8.50 7.50 1.00 0.00 0.00 Branch 125",
            "1.00 0.50 0.25 7.50 8.50",
        ]
    )

    service = AttendanceReportService(
        factory=ProcessorFactory(),
        ocr_service=lambda path: raw_text,
    )

    report = service.process("fake-b.pdf")

    assert len(report.rows) == 1
    assert report.rows[0].day == "Monday"
    assert report.rows[0].entry_time is not None
    assert report.rows[0].end_time is not None
    assert report.total_100 == 7.5
    assert report.total_125 == 0.25
    assert report.total_150 == 0.5
    assert report.total_saturday == 1.0
    assert pdf_path.exists()
