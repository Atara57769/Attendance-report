from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from processors.base_processor import BaseProcessor


class ProcessorA(BaseProcessor):

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

    def _build_report(self, rows, raw_text, lines):
        return AttendanceReport(
            rows=rows,
            total_hours=self.svc.extract_total_hours(raw_text),
            total_days=self.svc.extract_total_days(raw_text),
            hour_payment=self.svc.extract_hour_payment(raw_text),
            total_payment=self.svc.extract_total_payment(raw_text),
        )

    def _build_variated_row(self, row, e, x, h):
        return AttendanceRow(**{**row.__dict__, "entry_time": e, "end_time": x, "sum": h})

    def _finalize_variation(self, model, new_rows):
        return AttendanceReport(
            rows=new_rows,
            total_hours=self.time_variation.calculate_total_hours(new_rows),
            total_days=self.time_variation.calculate_total_days(new_rows),
            hour_payment=model.hour_payment,
            total_payment=model.total_payment,
        )

    def generate_pdf(self, model):
        return self.pdf_gen.create_report_a_pdf(model)