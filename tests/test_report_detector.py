import pytest

from core.exceptions import UnknownReportTypeError
from detectors import report_detector
from enums.report_type import ReportType


def test_match_any_true_and_false():
    assert report_detector._match_any([r"\b125\b"], "worked 125 hours") is True
    assert report_detector._match_any([r"\b150\b"], "worked 125 hours") is False


def test_detect_report_type_defaults_to_a_for_empty_or_invalid():
    assert report_detector.detect_report_type("") is ReportType.A
    assert report_detector.detect_report_type(None) is ReportType.A


def test_detect_report_type_b_when_only_b_patterns_match(monkeypatch):
    monkeypatch.setattr(report_detector, "_match_any", lambda patterns, text: patterns is report_detector.REPORT_B_PATTERNS)
    assert report_detector.detect_report_type("text") is ReportType.B


def test_detect_report_type_a_when_a_patterns_match(monkeypatch):
    monkeypatch.setattr(report_detector, "_match_any", lambda patterns, text: patterns is report_detector.REPORT_A_PATTERNS)
    assert report_detector.detect_report_type("text") is ReportType.A


def test_detect_report_type_b_when_fallback_numbers_present(monkeypatch):
    monkeypatch.setattr(report_detector, "_match_any", lambda patterns, text: False)
    assert report_detector.detect_report_type("something 150 something") is ReportType.B


def test_detect_report_type_wraps_errors(monkeypatch):
    monkeypatch.setattr(report_detector, "_match_any", lambda patterns, text: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(UnknownReportTypeError, match="Failed to detect report type: boom"):
        report_detector.detect_report_type("text")
