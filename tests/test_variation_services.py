import random
from datetime import date, time

import pytest

from core.exceptions import TransformationError
from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from variation.base_variation import BaseVariationService
from variation.validating_strategy_decorator import ValidatingStrategyDecorator
from variation.variation_a import VariationA
from variation.variation_b import VariationB


class DummyVariation(BaseVariationService):
    def __init__(self):
        self.raise_in_build = False
        self.raise_in_recalc = False

    def _build_row(self, row, e, x, rng):
        if self.raise_in_build:
            raise RuntimeError("build failed")
        return AttendanceRow(**{**row.__dict__, "entry_time": e, "end_time": x, "sum": self._calculate_hours(e, x)})

    def _recalculate_totals(self, original, rows):
        if self.raise_in_recalc:
            raise RuntimeError("recalc failed")
        return {"total_hours": round(sum(r.sum or 0 for r in rows), 2), "total_days": len(rows)}


def test_base_variation_apply_happy_path_and_default_seed():
    svc = DummyVariation()
    report = AttendanceReport(rows=[AttendanceRow(date=date(2026, 4, 29), entry_time=time(8, 0), end_time=time(16, 0))])
    result = svc.apply(report)
    assert result.total_days == 1
    assert result.rows[0].entry_time >= time(8, 0)


def test_get_seed_from_report_and_default():
    svc = DummyVariation()
    seeded = AttendanceReport(rows=[AttendanceRow(date=date(2026, 4, 29))])
    empty = AttendanceReport(rows=[])
    assert svc._get_seed_from_report(seeded) == 20260429
    assert svc._get_seed_from_report(empty) == 42


def test_process_row_returns_original_without_times():
    svc = DummyVariation()
    row = AttendanceRow(note="no times")
    assert svc._process_row(row, random.Random(1)) is row


def test_process_row_returns_original_on_build_failure():
    svc = DummyVariation()
    svc.raise_in_build = True
    row = AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))
    assert svc._process_row(row, random.Random(1)) is row


def test_shift_times_and_calculate_hours():
    svc = DummyVariation()
    rng = random.Random(1)
    entry, exit = svc._shift_times(time(8, 0), time(16, 0), rng)
    assert entry >= time(8, 0)
    assert exit >= time(16, 0)
    assert svc._calculate_hours(time(8, 0), time(16, 30)) == 8.5


def test_shift_times_wraps_errors():
    svc = DummyVariation()
    with pytest.raises(TransformationError, match="Failed to shift times"):
        svc._shift_times("bad", time(16, 0), random.Random(1))


def test_calculate_hours_returns_zero_on_failure():
    svc = DummyVariation()
    assert svc._calculate_hours("bad", time(16, 0)) == 0.0


def test_apply_wraps_recalculation_errors():
    svc = DummyVariation()
    svc.raise_in_recalc = True
    report = AttendanceReport(rows=[AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))])
    with pytest.raises(TransformationError, match="Failed to apply variation: recalc failed"):
        svc.apply(report, seed=1)


def test_variation_a_build_row_and_recalculate():
    svc = VariationA()
    row = AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0), sum=8.0)
    built = svc._build_row(row, time(8, 15), time(16, 45), random.Random(1))
    totals = svc._recalculate_totals(
        AttendanceReport(rows=[row], hour_payment=10.0, total_payment=80.0),
        [built],
    )
    assert built.entry_time == time(8, 15)
    assert totals["total_days"] == 1
    assert totals["hour_payment"] == 10.0


def test_variation_b_break_and_totals():
    svc = VariationB()
    shifted = svc._shift_break(time(0, 15), random.Random(1))
    assert shifted >= time(0, 15)
    assert svc._shift_break(None, random.Random(1)) is None
    assert svc._calculate_with_break(time(8, 0), time(17, 0), time(0, 30)) == 8.5
    assert svc._calculate_with_break(time(8, 0), time(7, 0), None) == 0.0
    totals = svc._recalculate_totals(
        AttendanceReport(rows=[], total_100=1.0, total_125=2.0, total_150=3.0, total_saturday=4.0),
        [AttendanceRow(sum=7.5)],
    )
    assert totals["total_hours"] == 7.5
    assert totals["total_100"] == 1.0


def test_validating_decorator_apply_happy_path():
    original = AttendanceReport(rows=[AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0), break_time=time(0, 15))])
    transformed = AttendanceReport(rows=[AttendanceRow(entry_time=time(8, 10), end_time=time(16, 10), break_time=time(0, 15))], total_hours=8.0)
    inner = type("Inner", (), {"apply": lambda self, report, seed=None: transformed})()
    result = ValidatingStrategyDecorator(inner).apply(original, seed=1)
    assert result.rows[0].entry_time == time(8, 10)


def test_validating_decorator_returns_original_when_inner_fails():
    original = AttendanceReport(rows=[AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))])
    inner = type("Inner", (), {"apply": lambda self, report, seed=None: (_ for _ in ()).throw(RuntimeError("boom"))})()
    assert ValidatingStrategyDecorator(inner).apply(original) is original


@pytest.mark.parametrize(
    ("row", "original_row", "expect_original"),
    [
        (AttendanceRow(entry_time=time(8, 0), end_time=time(7, 59)), AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0)), True),
        (AttendanceRow(entry_time=time(5, 59), end_time=time(16, 0)), AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0)), True),
        (AttendanceRow(entry_time=time(8, 0), end_time=time(23, 59), break_time=time(0, 25)), AttendanceRow(entry_time=time(8, 0), end_time=time(23, 30), break_time=time(0, 15)), True),
        (AttendanceRow(entry_time=time(8, 10), end_time=time(16, 5), break_time=time(0, 15)), AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0), break_time=time(0, 15)), False),
    ],
)
def test_validating_decorator_validate_row(row, original_row, expect_original):
    decorator = ValidatingStrategyDecorator(type("Inner", (), {"apply": lambda self, report, seed=None: report})())
    result = decorator._validate_row(row, original_row)
    if expect_original:
        assert result is original_row
    else:
        assert result is row


def test_validating_decorator_validate_row_handles_errors(monkeypatch):
    decorator = ValidatingStrategyDecorator(type("Inner", (), {"apply": lambda self, report, seed=None: report})())
    row = AttendanceRow(entry_time=time(8, 0), end_time=time(16, 0))
    monkeypatch.setattr(decorator, "_is_time_in_range", lambda *args: (_ for _ in ()).throw(RuntimeError("bad check")))
    assert decorator._validate_row(row, row) is row


def test_validating_decorator_helpers():
    decorator = ValidatingStrategyDecorator(type("Inner", (), {"apply": lambda self, report, seed=None: report})())
    assert decorator._is_time_in_range(time(8, 0), time(6, 0), time(23, 59)) is True
    assert decorator._time_diff_minutes(time(8, 30), time(8, 0)) == 30
    assert decorator._time_to_minutes(time(1, 15)) == 75
