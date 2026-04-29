"""
ValidatingStrategyDecorator - wraps transformation strategies with validation.

This decorator validates the transformed row before returning it:
- exit_time must be > entry_time
- entry/exit time change must be within 0-20 minutes
- break_time should be around 15 minutes (with tolerance)
- If validation fails, return the original row
"""
from datetime import time, timedelta
from typing import Optional
import logging

from core.models.attendance_report_models import AttendanceRow, AttendanceReport
from variation.base_variation import BaseVariationService

logger = logging.getLogger(__name__)


# Time boundaries configuration
TIME_MIN = time(6, 0)   # 06:00 - earliest allowed
TIME_MAX = time(23, 59) # 23:59 - latest allowed

# Variation constraints
MAX_VARIATION_MINUTES = 20  # Maximum allowed change in minutes
BREAK_TIME_TARGET = 15      # Target break time in minutes
BREAK_TIME_TOLERANCE = 5    # Tolerance in minutes (+/-)


class ValidatingStrategyDecorator:
    """
    Decorator that wraps a variation strategy with validation.
    
    The decorator implements the same interface as BaseVariationService,
    but adds validation after the inner strategy produces transformed rows.
    If validation fails, returns the original row.
    """
    
    def __init__(self, inner_strategy: BaseVariationService) -> None:
        """
        Initialize with an inner variation strategy.
        
        Args:
            inner_strategy: BaseVariationService instance to wrap
        """
        self._inner = inner_strategy
    
    def apply(self, report: AttendanceReport, seed: Optional[int] = None) -> AttendanceReport:
        """
        Apply variation and validate the result.
        
        Args:
            report: AttendanceReport to transform
            seed: Optional seed for deterministic random number generation
            
        Returns:
            AttendanceReport with validated transformed rows (or original if validation fails)
        """
        # Store original report for fallback
        original_report = report
        
        # Delegate to inner strategy first
        try:
            transformed_report = self._inner.apply(report, seed)
        except Exception as e:
            logger.warning(f"Inner strategy failed, returning original: {e}")
            return original_report
        
        # Validate each transformed row
        validated_rows: list[AttendanceRow] = []
        for i, row in enumerate(transformed_report.rows):
            original_row = report.rows[i] if i < len(report.rows) else row
            validated_row = self._validate_row(row, original_row)
            validated_rows.append(validated_row)
        
        # Return report with validated rows (preserve original totals)
        return transformed_report.__class__(
            rows=validated_rows,
            total_hours=transformed_report.total_hours,
            total_days=transformed_report.total_days,
            hour_payment=transformed_report.hour_payment,
            total_payment=transformed_report.total_payment,
            total_100=transformed_report.total_100,
            total_125=transformed_report.total_125,
            total_150=transformed_report.total_150,
            total_saturday=transformed_report.total_saturday,
            bonus=transformed_report.bonus,
            travel=transformed_report.travel,
        )
    
    def _validate_row(
        self,
        row: AttendanceRow,
        original_row: AttendanceRow | None = None,
    ) -> AttendanceRow:
        """
        Validate a single transformed row.
        
        Validations:
        1. exit_time > entry_time
        2. entry/exit time change must be within 0-20 minutes
        3. break_time should be around 15 minutes (with tolerance)
        
        Args:
            row: AttendanceRow to validate
            original_row: Original row for comparison
            
        Returns:
            The transformed row if valid, original row if validation fails
        """
        # Use original row for comparison if not provided
        if original_row is None:
            original_row = row
        
        try:
            # Skip validation if no times present
            if not row.entry_time or not row.end_time:
                return row
            
            # Validation 1: exit must be after entry
            if row.end_time <= row.entry_time:
                logger.warning(
                    f"Validation failed: end_time ({row.end_time}) <= entry_time ({row.entry_time})"
                )
                return original_row
            
            # Validation 2: times must be within allowed boundaries
            if not self._is_time_in_range(row.entry_time, TIME_MIN, TIME_MAX):
                logger.warning(
                    f"Validation failed: entry_time {row.entry_time} outside range [{TIME_MIN}, {TIME_MAX}]"
                )
                return original_row
            
            if not self._is_time_in_range(row.end_time, TIME_MIN, TIME_MAX):
                logger.warning(
                    f"Validation failed: end_time {row.end_time} outside range [{TIME_MIN}, {TIME_MAX}]"
                )
                return original_row
            
            # Validation 3: Check that time change is within 0-20 minutes
            if original_row.entry_time and original_row.end_time:
                entry_diff = abs(self._time_diff_minutes(row.entry_time, original_row.entry_time))
                exit_diff = abs(self._time_diff_minutes(row.end_time, original_row.end_time))
                
                if entry_diff > MAX_VARIATION_MINUTES or exit_diff > MAX_VARIATION_MINUTES:
                    logger.warning(
                        f"Validation failed: time change too large (entry: {entry_diff}min, exit: {exit_diff}min, max: {MAX_VARIATION_MINUTES}min)"
                    )
                    return original_row
            
            # Validation 4: break_time should be around 15 minutes (with tolerance)
            if row.break_time and original_row.break_time:
                break_minutes = self._time_to_minutes(row.break_time)
                target_minutes = BREAK_TIME_TARGET
                min_allowed = target_minutes - BREAK_TIME_TOLERANCE
                max_allowed = target_minutes + BREAK_TIME_TOLERANCE
                
                if break_minutes < min_allowed or break_minutes > max_allowed:
                    logger.warning(
                        f"Validation failed: break_time {row.break_time} ({break_minutes}min) not in range [{min_allowed}, {max_allowed}]"
                    )
                    return original_row
            
            return row
            
        except Exception as e:
            logger.error(f"Error during row validation: {e}")
            return original_row
    
    def _is_time_in_range(self, t: time, min_time: time, max_time: time) -> bool:
        """
        Check if a time is within the allowed range.
        
        Args:
            t: time to check
            min_time: minimum allowed time
            max_time: maximum allowed time
            
        Returns:
            True if time is in range, False otherwise
        """
        return min_time <= t <= max_time
    
    def _time_diff_minutes(self, t1: time, t2: time) -> int:
        """
        Calculate the difference between two times in minutes.
        
        Args:
            t1: First time
            t2: Second time
            
        Returns:
            Difference in minutes (t1 - t2)
        """
        from datetime import datetime
        dt1 = datetime.combine(datetime.today(), t1)
        dt2 = datetime.combine(datetime.today(), t2)
        diff = dt1 - dt2
        return int(diff.total_seconds() / 60)
    
    def _time_to_minutes(self, t: time) -> int:
        """
        Convert a time to total minutes.
        
        Args:
            t: time to convert
            
        Returns:
            Total minutes
        """
        return t.hour * 60 + t.minute
