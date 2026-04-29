from datetime import date, time

import pytest

from core.exceptions import PDFGenerationError, ParsingError, TransformationError
from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from processors.base_processor import BaseProcessor
from processors.processor_a import ProcessorA
from processors.processor_b import ProcessorB


class DummyBaseProcessor(BaseProcessor):
    def __init__(self):
        super().__init__(parsing_service=None, time_variation_service=None, pdf_generator=None)
        self.raise_on_parse = False
        self.raise_on_finalize = False

    def _parse_row(self, line):
        if self.raise_on_parse:
            raise RuntimeError("row failed")
        return AttendanceRow(note=line) if line.strip() else None

    def _build_report(self, rows, raw_text, lines):
        return AttendanceReport(rows=rows, total_days=len(rows))

    def _build_variated_row(self, row, e, x, h):
        return AttendanceRow(**{**row.__dict__, "entry_time": e, "end_time": x, "sum": h})

    def _finalize_variation(self, model, new_rows):
        if self.raise_on_finalize:
            raise RuntimeError("finalize failed")
        return AttendanceReport(rows=new_rows, total_days=len(new_rows))

    def generate_pdf(self, model):
        return "out.pdf"


class StubSvc:
    def normalize_line(self, line):
        return line

    def extract_day(self, line):
        return "Sunday"

    def extract_date(self, line):
        return date(2026, 4, 29)

    def extract_times(self, line):
        return [time(8, 0), time(16, 0)]

    def extract_numbers(self, line):
        return [8.0, 7.5, 1.0, 0.5, 0.0]

    def clean_text(self, line):
        return "clean"

    def extract_total_hours(self, raw):
        return 8.0

    def extract_total_days(self, raw):
        return 1

    def extract_hour_payment(self, raw):
        return 10.0

    def extract_total_payment(self, raw):
        return 80.0


class StubVariation:
    def apply_variation(self, entry, end):
        return time(8, 10), time(16, 10), 8.0

    def calculate_total_hours(self, rows):
        return 8.0

    def calculate_total_days(self, rows):
        return len(rows)

    def apply_break_variation(self, break_time):
        return time(0, 20)

    def calculate_hours_with_break(self, e, x, new_break):
        return 7.83


class StubPdfA:
    def create_report_a_pdf(self, model):
        return "a.pdf"


class StubPdfB:
    def create_report_b_pdf(self, model):
        return "b.pdf"


def test_base_processor_parse_and_apply_variation():
    processor = DummyBaseProcessor()
    report = processor.parse("one\n\ntwo")
    varied = processor.apply_variation(AttendanceReport(rows=[AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))]))
    assert [row.note for row in report.rows] == ["one", "two"]
    assert varied.total_days == 1


def test_base_processor_wraps_parse_and_variation_errors():
    processor = DummyBaseProcessor()
    processor.raise_on_parse = True
    with pytest.raises(ParsingError, match="Failed to parse report: row failed"):
        processor.parse("one")
    processor = DummyBaseProcessor()
    processor.raise_on_finalize = True
    with pytest.raises(TransformationError, match="Failed to apply variation: finalize failed"):
        processor.apply_variation(AttendanceReport(rows=[AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))]))


def test_base_processor_process_row_variation_passthroughs():
    processor = DummyBaseProcessor()
    processor.time_variation = StubVariation()
    row = AttendanceRow(note="no times")
    assert processor._process_row_variation(row) is row
    processor.time_variation = type("BadVariation", (), {"apply_variation": lambda self, e, x: (_ for _ in ()).throw(RuntimeError("boom"))})()
    timed_row = AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))
    assert processor._process_row_variation(timed_row) is timed_row


def test_processor_a_methods():
    processor = ProcessorA(StubSvc(), StubVariation(), StubPdfA())
    row = processor._parse_row("valid enough line")
    assert row.sum == 0.5
    assert processor._parse_row("Page 1") is None
    report = processor._build_report([AttendanceRow()], "raw", ["line"])
    assert report.total_payment == 80.0
    varied = processor._build_variated_row(AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0), sum=8.0), time(8, 5), time(16, 5), 8.0)
    assert varied.entry_time == time(8, 5)
    finalized = processor._finalize_variation(
        AttendanceReport(rows=[AttendanceRow()], hour_payment=10.0, total_payment=80.0),
        [AttendanceRow(sum=8.0)],
    )
    assert finalized.total_days == 1
    assert processor.generate_pdf(AttendanceReport(rows=[])) == "a.pdf"


def test_processor_a_error_paths():
    bad_svc = StubSvc()
    bad_svc.extract_total_hours = lambda raw: (_ for _ in ()).throw(RuntimeError("bad total"))
    processor = ProcessorA(bad_svc, StubVariation(), StubPdfA())
    with pytest.raises(ParsingError, match="Failed to build report: bad total"):
        processor._build_report([], "raw", [])
    bad_variation = type("BadVariation", (), {"calculate_total_hours": lambda self, rows: (_ for _ in ()).throw(RuntimeError("bad calc")), "calculate_total_days": lambda self, rows: 0})()
    processor = ProcessorA(StubSvc(), bad_variation, StubPdfA())
    with pytest.raises(ParsingError, match="Failed to finalize variation: bad calc"):
        processor._finalize_variation(AttendanceReport(rows=[]), [])
    processor = ProcessorA(StubSvc(), StubVariation(), type("BadPdf", (), {"create_report_a_pdf": lambda self, model: (_ for _ in ()).throw(RuntimeError("bad pdf"))})())
    with pytest.raises(PDFGenerationError, match="Failed to generate PDF: bad pdf"):
        processor.generate_pdf(AttendanceReport(rows=[]))


def test_processor_b_methods():
    processor = ProcessorB(StubSvc(), StubVariation(), StubPdfB())
    row = processor._parse_row("long enough 08:00 17:00 00:15 line")
    assert row.break_time == "00:15"
    assert processor._parse_row("Page 1 long enough") is None
    report = processor._build_report([AttendanceRow()], "raw", ["1.0 2.0 3.0 4.0 5.0"])
    assert report.total_hours == 5.0
    varied = processor._build_variated_row(AttendanceRow(entry_time="08:00", end_time="17:00", break_time="00:15", sum=8.0), "08:05", "17:05", None)
    assert varied.break_time == time(0, 20)
    finalized = processor._finalize_variation(
        AttendanceReport(rows=[AttendanceRow()], total_100=1.0, total_125=2.0, total_150=3.0, total_saturday=4.0),
        [AttendanceRow(sum=8.0)],
    )
    assert finalized.total_150 == 3.0
    assert processor.generate_pdf(AttendanceReport(rows=[])) == "b.pdf"


def test_processor_b_error_paths():
    processor = ProcessorB(StubSvc(), StubVariation(), StubPdfB())
    bad_variation = type("BadVariation", (), {"calculate_total_hours": lambda self, rows: (_ for _ in ()).throw(RuntimeError("bad calc")), "calculate_total_days": lambda self, rows: 0})()
    processor = ProcessorB(StubSvc(), bad_variation, StubPdfB())
    with pytest.raises(ParsingError, match="Failed to finalize variation: bad calc"):
        processor._finalize_variation(AttendanceReport(rows=[]), [])
    processor = ProcessorB(StubSvc(), StubVariation(), type("BadPdf", (), {"create_report_b_pdf": lambda self, model: (_ for _ in ()).throw(RuntimeError("bad pdf"))})())
    with pytest.raises(PDFGenerationError, match="Failed to generate PDF: bad pdf"):
        processor.generate_pdf(AttendanceReport(rows=[]))


def test_processor_pdf_generation_passthrough():
    processor_a = ProcessorA(StubSvc(), StubVariation(), type("PdfA", (), {"create_report_a_pdf": lambda self, model: (_ for _ in ()).throw(PDFGenerationError("pdf-a"))})())
    with pytest.raises(PDFGenerationError, match="pdf-a"):
        processor_a.generate_pdf(AttendanceReport(rows=[]))
    processor_b = ProcessorB(StubSvc(), StubVariation(), type("PdfB", (), {"create_report_b_pdf": lambda self, model: (_ for _ in ()).throw(PDFGenerationError("pdf-b"))})())
    with pytest.raises(PDFGenerationError, match="pdf-b"):
        processor_b.generate_pdf(AttendanceReport(rows=[]))
