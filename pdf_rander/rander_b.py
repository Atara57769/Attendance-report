from datetime import datetime
from reportlab.platypus import Table, Paragraph
from pdf_rander.base_rander import BasePDFService

class PDFServiceB(BasePDFService):  # noqa: F821

    def _build_filename(self):
        return f"report_b_{datetime.now().strftime('%Y%m%d_%H%M%S')}"  # noqa: F821

    def _summary(self, report):
        data = [
            ["Metric", "Value"],
            ["Total Hours", report.total_hours or 0],
            ["Total Days", report.total_days or 0],
            ["100%", report.total_100 or 0],
            ["125%", report.total_125 or 0],
            ["150%", report.total_150 or 0],
            ["Saturday", report.total_saturday or 0],
        ]

        table = Table(data)
        table.setStyle(self._table_style())
        return table

    def _table(self, report):
        data = [["Date", "Day", "Entry", "End", "Break", "Hours"]]

        for r in report.rows:
            data.append([
                r.date or "-",
                r.day or "-",
                str(r.entry_time) if r.entry_time else "-",
                str(r.end_time) if r.end_time else "-",
                str(r.break_time) if r.break_time else "-",
                r.sum or "-"
            ])

        table = Table(data)
        table.setStyle(self._table_style())
        return table

    def _conclusion(self, report):
        return Paragraph(
            f"""
            <b>Conclusion</b><br/>
            Total Hours: {report.total_hours or 0}<br/>
            100%: {report.total_100 or 0}<br/>
            125%: {report.total_125 or 0}<br/>
            150%: {report.total_150 or 0}
            """,
            self.styles['Normal']
        )