import re
from typing import Optional
from datetime import datetime, timedelta
import random

from core.models.attendance_report_A_models import AttendanceReportA, AttendanceRowA
from processores.parse_processor import AttendanceParsingService
from services.pdf_generator import PDFGenerator
from services.time_variation_service import TimeVariationService


class ProcessorA:

    def __init__(self):
        self.svc = AttendanceParsingService()

    def parse(self, raw_text: str):
        report = AttendanceReportA()
        lines = raw_text.strip().split('\n')

        report.total_hours = self.svc.extract_total_hours(raw_text)
        report.total_days = self.svc.extract_total_days(raw_text)
        report.hour_payment = self.svc.extract_hour_payment(raw_text)
        report.total_payment = self.svc.extract_total_payment(raw_text)

        report.rows = [r for r in (self._parse_row(l) for l in lines) if r]
        return report

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

        return AttendanceRowA(
            date=date,
            day=day,
            entry_time=entry,
            end_time=end,
            sum=min(hours),
            note=self.svc.clean_text(line) or None
        )
    


    def apply_variation(self, model: AttendanceReportA) -> AttendanceReportA:
        for row in model.rows:
            if row.entry_time and row.end_time:
                e, x, h = TimeVariationService.apply_variation(
                    row.entry_time,
                    row.end_time
                )

                if e and x:
                    row.entry_time = e
                    row.end_time = x
                    row.sum = h

        model.total_hours = TimeVariationService.calculate_total_hours(model.rows)
        model.total_days = TimeVariationService.calculate_total_days(model.rows)

        return model

    def generate_pdf(self, model: AttendanceReportA, output_dir: str = "output", filename: str = None) -> str:
        """
        Generate PDF report for AttendanceReportA with table and conclusions.
        
        """
        pdf_gen = PDFGenerator(output_dir)
        return pdf_gen.create_report_a_pdf(model, filename)