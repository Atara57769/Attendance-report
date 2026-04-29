from datetime import datetime

from reportlab.platypus import Table, Paragraph

from core.models.attendance_report_models import AttendanceReport
from pdf_render.base_render import BasePDFService


class PDFServiceA(BasePDFService):

    def _build_filename(self) -> str:
        return f"report_a_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _summary(self, report: AttendanceReport) -> Table:
        data = [
            ["Metric", "Value"],
            ["Total Hours", report.total_hours or 0],
            ["Total Days", report.total_days or 0],
            ["Hourly Payment", f"${report.hour_payment or 0:.2f}"],
            ["Total Payment", f"${report.total_payment or 0:.2f}"],
        ]

        table = Table(data)
        table.setStyle(self._table_style())
        return table

    def _table(self, report: AttendanceReport) -> Table:
        data = [["Date", "Day", "Entry", "End", "Hours", "Notes"]]

        for r in report.rows:
            data.append([
                r.date or "-",
                r.day or "-",
                str(r.entry_time) if r.entry_time else "-",
                str(r.end_time) if r.end_time else "-",
                r.sum or "-",
                r.note or "-"
            ])

        table = Table(data)
        table.setStyle(self._table_style())
        return table

    def _conclusion(self, report: AttendanceReport) -> Paragraph:
        return Paragraph(
            f"""
            <b>Conclusion</b><br/>
            Total: {report.total_hours or 0} hours<br/>
            Payment: ${report.total_payment or 0:.2f}
            """,
            self.styles['Normal']
        )
