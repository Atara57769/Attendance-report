
import re
from typing import Optional
from datetime import datetime, timedelta
import random

from core.models.attendance_report_B_models import AttendanceReportB, AttendanceRowB
from processores.parse_processor import AttendanceParsingService
from services.pdf_generator import PDFGenerator
from services.time_variation_service import TimeVariationService


class ProcessorB:

    def __init__(self):
        self.svc = AttendanceParsingService()

    def parse(self, raw_text: str):
        report = AttendanceReportB()
        lines = raw_text.strip().split('\n')

        report.rows = [r for r in (self._parse_row(l) for l in lines) if r]

        totals_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d{1,2}:\d{2})'

        for line in reversed(lines):
            match = re.search(totals_pattern, line)
            if match:
                report.total_saturday = float(match.group(1))
                report.total_150 = float(match.group(2))
                report.total_125 = float(match.group(3))
                report.total_100 = float(match.group(4))
                report.total_hours = float(match.group(5))
                break

        report.bonus = 0.0
        report.travel = 0.0

        return report

    def _parse_row(self, line: str):
        if not line or len(line.strip()) < 10 or "Page" in line:
            return None

        line = self.svc.normalize_line(line)

        day = self.svc.extract_day(line)
        if not day:
            return None

        times = re.findall(r"\d{1,2}[:.]\d{2}", line)
        if len(times) < 2:
            return None

        times = [t.replace(".", ":") for t in times]

        nums = self.svc.extract_numbers(line)
        nums = [n for n in nums if 0 <= n <= 24]

        if not nums:
            return None

        return AttendanceRowB(
            date=self.svc.extract_date(line),
            day=day,
            entry_time=times[0],
            end_time=times[1],
            break_time=times[2] if len(times) > 2 else "00:00",
            sum=nums[0],
            col_100=nums[1] if len(nums) > 1 else 0.0,
            col_125=nums[2] if len(nums) > 2 else 0.0,
            col_150=nums[3] if len(nums) > 3 else 0.0,
            col_saturday=nums[4] if len(nums) > 4 else 0.0,
            location=self.svc.clean_text(line)
        )
   
    def apply_variation(self, model: AttendanceReportB) -> AttendanceReportB:
        total_100 = total_125 = total_150 = total_saturday = 0.0

        for row in model.rows:
            if not row.entry_time or not row.end_time:
                continue

            e, x, _ = TimeVariationService.apply_variation(
                row.entry_time,
                row.end_time
            )

            if not e or not x:
                continue

            row.entry_time = e
            row.end_time = x

            if row.break_time:
                row.break_time = TimeVariationService.apply_break_variation(row.break_time)

            row.sum = TimeVariationService.calculate_hours_with_break(
                row.entry_time,
                row.end_time,
                row.break_time
            )

            # same logic as before
            if row.col_100:
                row.col_100 = round(row.sum * 1.0, 2)
                total_100 += row.col_100

            if row.col_125:
                row.col_125 = round(row.sum * 1.25, 2)
                total_125 += row.col_125

            if row.col_150:
                row.col_150 = round(row.sum * 1.5, 2)
                total_150 += row.col_150

            if row.col_saturday:
                row.col_saturday = round(row.sum * 1.5, 2)
                total_saturday += row.col_saturday

            total_100 += row.col_100
            total_125 += row.col_125
            total_150 += row.col_150
            total_saturday += row.col_saturday

        model.total_hours = TimeVariationService.calculate_total_hours(model.rows)
        model.total_days = TimeVariationService.calculate_total_days(model.rows)

        model.total_100 = round(total_100, 2)
        model.total_125 = round(total_125, 2)
        model.total_150 = round(total_150, 2)
        model.total_saturday = round(total_saturday, 2)

        return model
    def generate_pdf(self, model: AttendanceReportB, output_dir: str = "output", filename: str = None) -> str:
        """
        Generate PDF report for AttendanceReportB with table and conclusions.
        
        """
        pdf_gen = PDFGenerator(output_dir)
        return pdf_gen.create_report_b_pdf(model, filename)