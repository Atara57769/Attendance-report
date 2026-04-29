import pytest

from core.exceptions import ConfigurationError, UnknownReportTypeError
from core.models.attendance_report_models import AttendanceReport
from enums.report_type import ReportType
from factory import processor_factory as factory_module
from factory.processor_factory import ProcessorFactory
from processors.report_processor import ReportProcessor


def test_report_processor_delegates():
    parser = type("Parser", (), {"parse": lambda self, text: AttendanceReport(rows=[])})()
    variation = type("Variation", (), {"apply": lambda self, report, seed=None: AttendanceReport(rows=report.rows, total_days=seed)})()
    pdf = type("Pdf", (), {"generate": lambda self, report: "out.pdf"})()
    processor = ReportProcessor(parser=parser, variation_service=variation, pdf_service=pdf)
    report = processor.parse("raw")
    varied = processor.apply_variation(report, seed=7)
    path = processor.generate_pdf(report)
    assert isinstance(report, AttendanceReport)
    assert varied.total_days == 7
    assert path == "out.pdf"


def test_factory_create_a_and_b(monkeypatch):
    monkeypatch.setattr(factory_module, "ParserA", lambda: "parser-a")
    monkeypatch.setattr(factory_module, "ParserB", lambda: "parser-b")
    monkeypatch.setattr(factory_module, "VariationA", lambda: "variation-a")
    monkeypatch.setattr(factory_module, "VariationB", lambda: "variation-b")
    monkeypatch.setattr(factory_module, "ValidatingStrategyDecorator", lambda inner: ("decorated", inner))
    monkeypatch.setattr(factory_module, "PDFServiceA", lambda: "pdf-a")
    monkeypatch.setattr(factory_module, "PDFServiceB", lambda: "pdf-b")
    monkeypatch.setattr(factory_module, "ReportProcessor", lambda parser, variation_service, pdf_service: (parser, variation_service, pdf_service))
    factory = ProcessorFactory()
    assert factory._create_a() == ("parser-a", ("decorated", "variation-a"), "pdf-a")
    assert factory._create_b() == ("parser-b", ("decorated", "variation-b"), "pdf-b")


def test_factory_create_wraps_errors(monkeypatch):
    monkeypatch.setattr(factory_module, "ParserA", lambda: (_ for _ in ()).throw(RuntimeError("bad parser")))
    factory = ProcessorFactory()
    with pytest.raises(ConfigurationError, match="Failed to create ProcessorA: bad parser"):
        factory._create_a()


def test_factory_get_happy_path(monkeypatch):
    factory = ProcessorFactory()
    monkeypatch.setattr(factory, "_create_a", lambda: "processor-a")
    factory._map[ReportType.A] = factory._create_a
    assert factory.get(ReportType.A) == "processor-a"


def test_factory_get_errors():
    factory = ProcessorFactory()
    with pytest.raises(UnknownReportTypeError, match="Report type cannot be None"):
        factory.get(None)
    with pytest.raises(UnknownReportTypeError, match="No processor for type C"):
        factory.get("C")


def test_factory_get_wraps_unexpected_errors():
    factory = ProcessorFactory()
    factory._map[ReportType.A] = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    with pytest.raises(ConfigurationError, match="Failed to build processor: boom"):
        factory.get(ReportType.A)
