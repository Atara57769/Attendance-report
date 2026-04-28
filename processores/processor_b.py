
import re
from typing import Optional
from datetime import datetime, timedelta
import random

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from processores.parse_processor import AttendanceParsingService
from services.pdf_generator import PDFGenerator
from services.time_variation_service import TimeVariationService


class ProcessorB:

    def __init__(self):
        self.svc = AttendanceParsingService()

    def parse(self, raw_text: str):
        lines = raw_text.strip().split('\n')

        rows = [r for r in (self._parse_row(l) for l in lines) if r]

        totals_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d{1,2}:\d{2})'

        total_saturday = total_150 = total_125 = total_100 = total_hours = None

        for line in reversed(lines):
            match = re.search(totals_pattern, line)
            if match:
                total_saturday = float(match.group(1))
                total_150 = float(match.group(2))
                total_125 = float(match.group(3))
                total_100 = float(match.group(4))
                total_hours = float(match.group(5))
                break

        return AttendanceReport(
            rows=rows,
            total_hours=total_hours,
            total_days=None,
            hour_payment=None,
            total_payment=None,
            total_100=total_100,
            total_125=total_125,
            total_150=total_150,
            total_saturday=total_saturday,
            bonus=0.0,
            travel=0.0,
        )

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

        return AttendanceRow(
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
   
    def apply_variation(self, model: AttendanceReport) -> AttendanceReport:
        total_100 = total_125 = total_150 = total_saturday = 0.0
        new_rows = []

        for row in model.rows:
            if not row.entry_time or not row.end_time:
                new_rows.append(row)
                continue

            e, x, _ = TimeVariationService.apply_variation(
                row.entry_time,
                row.end_time
            )

            if not e or not x:
                new_rows.append(row)
                continue

            new_break_time = row.break_time
            if row.break_time:
                new_break_time = TimeVariationService.apply_break_variation(row.break_time)

            new_sum = TimeVariationService.calculate_hours_with_break(
                e,
                x,
                new_break_time
            )

            # Calculate columns
            new_col_100 = row.col_100
            new_col_125 = row.col_125
            new_col_150 = row.col_150
            new_col_saturday = row.col_saturday

            if new_col_100:
                new_col_100 = round(new_sum * 1.0, 2)
                total_100 += new_col_100

            if new_col_125:
                new_col_125 = round(new_sum * 1.25, 2)
                total_125 += new_col_125

            if new_col_150:
                new_col_150 = round(new_sum * 1.5, 2)
                total_150 += new_col_150

            if new_col_saturday:
                new_col_saturday = round(new_sum * 1.5, 2)
                total_saturday += new_col_saturday

            new_rows.append(AttendanceRow(
                date=row.date,
                day=row.day,
                entry_time=e,
                end_time=x,
                sum=new_sum,
                note=row.note,
                location=row.location,
                break_time=new_break_time,
                col_100=new_col_100,
                col_125=new_col_125,
                col_150=new_col_150,
                col_saturday=new_col_saturday,
            ))

        total_hours = TimeVariationService.calculate_total_hours(new_rows)
        total_days = TimeVariationService.calculate_total_days(new_rows)

        return AttendanceReport(
            rows=new_rows,
            total_hours=total_hours,
            total_days=total_days,
            hour_payment=model.hour_payment,
            total_payment=model.total_payment,
            total_100=round(total_100, 2),
            total_125=round(total_125, 2),
            total_150=round(total_150, 2),
            total_saturday=round(total_saturday, 2),
            bonus=model.bonus,
            travel=model.travel,
        )
    def generate_pdf(self, model: AttendanceReport, output_dir: str = "output", filename: str = None) -> str:
        """
        Generate PDF report for AttendanceReport with table and conclusions.
        
        """
        pdf_gen = PDFGenerator(output_dir)
        return pdf_gen.create_report_b_pdf(model, filename)