from datetime import date, time

import pytest

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from parse.base_parser import BaseParsingService
from parse.parser_a import ParserA
from parse.parser_b import ParserB


class DummyParser(BaseParsingService):
    def __init__(self):
        self.fail_parse_row = False
        self.build_result = AttendanceReport(rows=[])

    def parse_row(self, line: str):
        if self.fail_parse_row:
            raise RuntimeError("row failed")
        return AttendanceRow(note=line) if line.strip() else None

    def build_report(self, rows, raw_text, lines):
        return AttendanceReport(rows=rows, total_days=len(lines))


def test_base_parse_happy_path():
    parser = DummyParser()
    result = parser.parse("line1\n\nline2")
    assert [row.note for row in result.rows] == ["line1", "line2"]
    assert result.total_days == 3


def test_base_parse_wraps_errors():
    parser = DummyParser()
    parser.fail_parse_row = True
    with pytest.raises(ValueError, match="Failed to parse report: row failed"):
        parser.parse("line1")


def test_normalize_line():
    assert BaseParsingService.normalize_line(" a |  b   c ") == "a b c"


def test_extract_times_parses_colon_dot_and_compact_formats():
    result = BaseParsingService.extract_times("08:30 9.45 1730 2460 99")
    assert result == [time(8, 30), time(9, 45), time(17, 30)]


def test_extract_times_returns_empty_on_regex_failure(monkeypatch):
    monkeypatch.setattr("parse.base_parser.re.findall", lambda pattern, text: (_ for _ in ()).throw(RuntimeError("regex failed")))
    assert BaseParsingService.extract_times("08:30") == []


def test_extract_numbers_handles_decimals_and_compact_hours():
    assert BaseParsingService.extract_numbers("7 830 12.5") == [7.0, 8.3, 12.5]


def test_extract_numbers_returns_empty_on_failure(monkeypatch):
    monkeypatch.setattr("parse.base_parser.re.findall", lambda pattern, text: (_ for _ in ()).throw(RuntimeError("regex failed")))
    assert BaseParsingService.extract_numbers("1 2 3") == []


def test_extract_day_returns_match_and_none(monkeypatch):
    class Match:
        def group(self, index):
            return "Sunday"

    monkeypatch.setattr("parse.base_parser.re.search", lambda pattern, text: Match())
    assert BaseParsingService.extract_day("line") == "Sunday"
    monkeypatch.setattr("parse.base_parser.re.search", lambda pattern, text: None)
    assert BaseParsingService.extract_day("line") is None


def test_extract_date_supports_implicit_and_two_digit_year(monkeypatch):
    class FakeNow:
        year = 2026

    class Match:
        def __init__(self, value):
            self.value = value

        def group(self, index):
            return self.value

    monkeypatch.setattr("parse.base_parser.datetime", type("FakeDateTime", (), {"now": staticmethod(lambda: FakeNow())}))
    monkeypatch.setattr("parse.base_parser.re.search", lambda pattern, text: Match("3/4"))
    assert BaseParsingService.extract_date("line") == date(2026, 4, 3)
    monkeypatch.setattr("parse.base_parser.re.search", lambda pattern, text: Match("3-4-26"))
    assert BaseParsingService.extract_date("line") == date(2026, 4, 3)


def test_extract_date_returns_none_when_invalid(monkeypatch):
    monkeypatch.setattr("parse.base_parser.re.search", lambda pattern, text: None)
    assert BaseParsingService.extract_date("line") is None


def test_clean_text_removes_numbers_and_punctuation():
    assert BaseParsingService.clean_text("abc 12:30 !!!") == "abc"


def test_clean_text_returns_original_on_failure(monkeypatch):
    monkeypatch.setattr("parse.base_parser.re.sub", lambda pattern, repl, text: (_ for _ in ()).throw(RuntimeError("bad sub")))
    assert BaseParsingService.clean_text("abc") == "abc"


@pytest.mark.parametrize(
    ("method_name", "expected"),
    [
        ("extract_total_hours", 1234.5),
        ("extract_hour_payment", 1234.5),
        ("extract_total_payment", 1234.5),
    ],
)
def test_text_total_extractors(monkeypatch, method_name, expected):
    class Match:
        def group(self, index):
            return "1,234.5" if index == 1 else None

    monkeypatch.setattr("parse.base_parser.re.search", lambda *args, **kwargs: Match())
    assert getattr(BaseParsingService, method_name)("text") == expected


def test_extract_total_days(monkeypatch):
    class Match:
        def group(self, index):
            return "7" if index == 1 else None

    monkeypatch.setattr("parse.base_parser.re.search", lambda *args, **kwargs: Match())
    assert BaseParsingService.extract_total_days("text") == 7


def test_total_extractors_return_none_on_failure(monkeypatch):
    monkeypatch.setattr("parse.base_parser.re.search", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("bad search")))
    assert BaseParsingService.extract_total_hours("text") is None
    assert BaseParsingService.extract_total_days("text") is None
    assert BaseParsingService.extract_hour_payment("text") is None
    assert BaseParsingService.extract_total_payment("text") is None


def test_parser_a_parse_row_happy_path(monkeypatch):
    parser = ParserA()
    monkeypatch.setattr(parser, "extract_day", lambda line: "Sunday")
    monkeypatch.setattr(parser, "extract_date", lambda line: date(2026, 4, 29))
    monkeypatch.setattr(parser, "extract_times", lambda line: [time(8, 0), time(16, 0)])
    monkeypatch.setattr(parser, "extract_numbers", lambda line: [8.0, 16.0, 7.5])
    monkeypatch.setattr(parser, "clean_text", lambda line: "clean note")
    row = parser.parse_row("valid line")
    assert row == AttendanceRow(
        date=date(2026, 4, 29),
        day="Sunday",
        entry_time=time(8, 0),
        end_time=time(16, 0),
        sum=7.5,
        note="clean note",
    )


def test_parser_a_parse_row_returns_none_for_invalid_inputs(monkeypatch):
    parser = ParserA()
    assert parser.parse_row("Page 1") is None
    monkeypatch.setattr(parser, "extract_day", lambda line: None)
    assert parser.parse_row("valid line") is None


def test_parser_a_build_report():
    parser = ParserA()
    report = parser.build_report([AttendanceRow()], "raw", ["line"])
    assert isinstance(report, AttendanceReport)


def test_parser_b_parse_row_happy_path(monkeypatch):
    parser = ParserB()
    monkeypatch.setattr(parser, "extract_day", lambda line: "Monday")
    monkeypatch.setattr(parser, "extract_date", lambda line: date(2026, 4, 29))
    monkeypatch.setattr(parser, "extract_numbers", lambda line: [8.0, 6.0, 1.0, 0.5, 0.0])
    monkeypatch.setattr(parser, "clean_text", lambda line: "location")
    row = parser.parse_row("Monday 01/04 08:00 17:00 00:15")
    assert row == AttendanceRow(
        date=date(2026, 4, 29),
        day="Monday",
        entry_time=time(8, 0),
        end_time=time(17, 0),
        break_time=time(0, 15),
        sum=8.0,
        col_100=6.0,
        col_125=1.0,
        col_150=0.5,
        col_saturday=0.0,
        location="location",
    )


def test_parser_b_parse_row_returns_none_for_invalid_inputs(monkeypatch):
    parser = ParserB()
    assert parser.parse_row("short") is None
    monkeypatch.setattr(parser, "extract_day", lambda line: None)
    assert parser.parse_row("Monday 08:00 17:00") is None


def test_parser_b_build_report_extracts_last_totals_line():
    parser = ParserB()
    report = parser.build_report(
        [AttendanceRow()],
        "raw",
        ["ignore", "1.0 2.0 3.0 4.0 5.0"],
    )
    assert report.total_saturday == 1.0
    assert report.total_150 == 2.0
    assert report.total_125 == 3.0
    assert report.total_100 == 4.0
    assert report.total_hours == 5.0
