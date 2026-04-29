import re
from typing import Optional
from datetime import datetime, timedelta
import random

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from processores.parse_processor import AttendanceParsingService
from services.pdf_generator import PDFGenerator
from services.time_variation_service import TimeVariationService


class ProcessorA:

    def __init__(self):
        self.svc = AttendanceParsingService()

    def parse(self, raw_text: str):
        lines = raw_text.strip().split('\n')

        rows = [r for r in (self._parse_row(l) for l in lines) if r]

        return AttendanceReport(
            rows=rows,
            total_hours=self.svc.extract_total_hours(raw_text),
            total_days=self.svc.extract_total_days(raw_text),
            hour_payment=self.svc.extract_hour_payment(raw_text),
            total_payment=self.svc.extract_total_payment(raw_text),
        )

    def _parse_row(self, line: str):
        if not line or len(line.strip()) < 5 or "Page" in line:
            return None

        line = self.svc.normalize_line(line)

        day = self.svc.extract_day(line)
        if not day:
            return None

        date = self.svc.extract_date(line)
        times = self.svc.extract_times(line)
        nums = self.svc.extract_numbers(line)

        if not times or not nums:
            return None

        entry = times[0]
        end = times[1] if len(times) > 1 else entry

        hours = [n for n in nums if 0 < n <= 12]
        if not hours:
            return None

        return AttendanceRow(
            date=date,
            day=day,
            entry_time=entry,
            end_time=end,
            sum=min(hours),
            note=self.svc.clean_text(line) or None
        )
    


    def apply_variation(self, model: AttendanceReport) -> AttendanceReport:
        new_rows = []
        for row in model.rows:
            if row.entry_time and row.end_time:
                e, x, h = TimeVariationService.apply_variation(
                    row.entry_time,
                    row.end_time
                )

                if e and x:
                    new_rows.append(AttendanceRow(
                        date=row.date,
                        day=row.day,
                        entry_time=e,
                        end_time=x,
                        sum=h,
                        note=row.note,
                        location=row.location,
                        break_time=row.break_time,
                        col_100=row.col_100,
                        col_125=row.col_125,
                        col_150=row.col_150,
                        col_saturday=row.col_saturday,
                    ))
                else:
                    new_rows.append(row)
            else:
                new_rows.append(row)

        total_hours = TimeVariationService.calculate_total_hours(new_rows)
        total_days = TimeVariationService.calculate_total_days(new_rows)

        return AttendanceReport(
            rows=new_rows,
            total_hours=total_hours,
            total_days=total_days,
            hour_payment=model.hour_payment,
            total_payment=model.total_payment,
            total_100=model.total_100,
            total_125=model.total_125,
            total_150=model.total_150,
            total_saturday=model.total_saturday,
            bonus=model.bonus,
            travel=model.travel,
        )

    def generate_pdf(self, model: AttendanceReport) -> str:
        """
        Generate PDF report for AttendanceReport with table and conclusions.
        
        """
        pdf_gen = PDFGenerator()
        return pdf_gen.create_report_a_pdf(model)