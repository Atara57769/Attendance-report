from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import List

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER


class BasePDFService(ABC):

    def __init__(self, output_dir="../output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.styles = getSampleStyleSheet()
        self._setup_styles()

    # ---------- PUBLIC ----------
    def generate(self, report) -> str:
        filename = self._build_filename()
        elements = self._build_elements(report)

        return self._build_pdf(elements, filename)

    # ---------- TEMPLATE METHOD ----------
    def _build_elements(self, report):
        elements = []

        elements.append(self._title())
        elements.append(self._subtitle())
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(self._summary(report))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(self._table(report))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(self._conclusion(report))

        return elements

    # ---------- ABSTRACT ----------
    @abstractmethod
    def _summary(self, report): ...

    @abstractmethod
    def _table(self, report): ...

    @abstractmethod
    def _conclusion(self, report): ...

    @abstractmethod
    def _build_filename(self) -> str: ...

    # ---------- COMMON ----------
    def _build_pdf(self, elements: List, filename: str) -> str:
        path = self.output_dir / f"{filename}.pdf"

        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        doc.build(elements)
        return str(path)

    def _title(self):
        return Paragraph("Attendance Report", self.styles['TitleCustom'])

    def _subtitle(self):
        return Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Subtitle']
        )

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='TitleCustom',
            fontSize=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))

        self.styles.add(ParagraphStyle(
            name='Subtitle',
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))

    def _table_style(self):
        from reportlab.platypus import TableStyle

        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])