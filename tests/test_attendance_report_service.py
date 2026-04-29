import pytest

from core.exceptions import (
    OCRProcessingError,
    PDFGenerationError,
    ParsingError,
    TransformationError,
    UnknownReportTypeError,
)
from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from enums.report_type import ReportType
from services import attendance_report_service as service_module
from services.attendance_report_service import AttendanceReportService


class StubProcessor:
    def __init__(
        self,
        parsed_model=None,
        parse_error=None,
        variation_result=None,
        variation_error=None,
        pdf_path="out.pdf",
        pdf_error=None,
    ):
        self.parsed_model = parsed_model or AttendanceReport(rows=[AttendanceRow()])
        self.parse_error = parse_error
        self.variation_result = variation_result or self.parsed_model
        self.variation_error = variation_error
        self.pdf_path = pdf_path
        self.pdf_error = pdf_error
        self.parse_calls = []
        self.variation_calls = []
        self.pdf_calls = []

    def parse(self, raw_text):
        self.parse_calls.append(raw_text)
        if self.parse_error:
            raise self.parse_error
        return self.parsed_model

    def apply_variation(self, model):
        self.variation_calls.append(model)
        if self.variation_error:
            raise self.variation_error
        return self.variation_result

    def generate_pdf(self, model):
        self.pdf_calls.append(model)
        if self.pdf_error:
            raise self.pdf_error
        return self.pdf_path


class StubFactory:
    def __init__(self, processor=None, error=None):
        self.processor = processor
        self.error = error
        self.calls = []

    def get(self, report_type):
        self.calls.append(report_type)
        if self.error:
            raise self.error
        return self.processor


def test_process_happy_path(monkeypatch):
    parsed = AttendanceReport(rows=[AttendanceRow(note="parsed")])
    varied = AttendanceReport(rows=[AttendanceRow(note="varied")])
    processor = StubProcessor(parsed_model=parsed, variation_result=varied)
    factory = StubFactory(processor=processor)
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)

    service = AttendanceReportService(factory=factory, ocr_service=lambda path: "raw-text")

    result = service.process("report.pdf")

    assert result is varied
    assert factory.calls == [ReportType.A]
    assert processor.parse_calls == ["raw-text"]
    assert processor.variation_calls == [parsed]
    assert processor.pdf_calls == [varied]


def test_process_ocr_file_not_found():
    service = AttendanceReportService(
        factory=StubFactory(processor=StubProcessor()),
        ocr_service=lambda path: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )

    with pytest.raises(OCRProcessingError, match="PDF file not found: report.pdf"):
        service.process("report.pdf")


def test_process_ocr_failure():
    service = AttendanceReportService(
        factory=StubFactory(processor=StubProcessor()),
        ocr_service=lambda path: (_ for _ in ()).throw(RuntimeError("ocr crash")),
    )

    with pytest.raises(OCRProcessingError, match="Failed to process PDF: ocr crash"):
        service.process("report.pdf")


def test_process_detect_report_type_failure(monkeypatch):
    monkeypatch.setattr(
        service_module,
        "detect_report_type",
        lambda text: (_ for _ in ()).throw(RuntimeError("detect failed")),
    )
    service = AttendanceReportService(
        factory=StubFactory(processor=StubProcessor()),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(UnknownReportTypeError, match="Failed to detect report type: detect failed"):
        service.process("report.pdf")


def test_process_factory_failure(monkeypatch):
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.B)
    service = AttendanceReportService(
        factory=StubFactory(error=RuntimeError("factory failed")),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(
        UnknownReportTypeError,
        match="Failed to get processor for type ReportType.B: factory failed",
    ):
        service.process("report.pdf")


def test_process_parse_error_passthrough(monkeypatch):
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)
    processor = StubProcessor(parse_error=ParsingError("bad parse"))
    service = AttendanceReportService(
        factory=StubFactory(processor=processor),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(ParsingError, match="bad parse"):
        service.process("report.pdf")


def test_process_parse_error_wrapped(monkeypatch):
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)
    processor = StubProcessor(parse_error=ValueError("bad parse"))
    service = AttendanceReportService(
        factory=StubFactory(processor=processor),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(ParsingError, match="Failed to parse report: bad parse"):
        service.process("report.pdf")


def test_process_variation_validation_failure_falls_back(monkeypatch):
    parsed = AttendanceReport(rows=[AttendanceRow(note="parsed")])
    processor = StubProcessor(parsed_model=parsed, variation_error=TransformationError("invalid variation"))
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)
    service = AttendanceReportService(
        factory=StubFactory(processor=processor),
        ocr_service=lambda path: "raw-text",
    )

    result = service.process("report.pdf")

    assert result is parsed
    assert processor.pdf_calls == [parsed]


def test_process_variation_failure_wrapped(monkeypatch):
    processor = StubProcessor(variation_error=RuntimeError("variation crash"))
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)
    service = AttendanceReportService(
        factory=StubFactory(processor=processor),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(TransformationError, match="Failed to apply variation: variation crash"):
        service.process("report.pdf")


def test_process_pdf_generation_error_passthrough(monkeypatch):
    processor = StubProcessor(pdf_error=PDFGenerationError("pdf failed"))
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)
    service = AttendanceReportService(
        factory=StubFactory(processor=processor),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(PDFGenerationError, match="pdf failed"):
        service.process("report.pdf")


def test_process_pdf_generation_error_wrapped(monkeypatch):
    processor = StubProcessor(pdf_error=RuntimeError("pdf crash"))
    monkeypatch.setattr(service_module, "detect_report_type", lambda text: ReportType.A)
    service = AttendanceReportService(
        factory=StubFactory(processor=processor),
        ocr_service=lambda path: "raw-text",
    )

    with pytest.raises(PDFGenerationError, match="Failed to generate PDF: pdf crash"):
        service.process("report.pdf")
