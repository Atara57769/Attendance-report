"""PDF generation service for attendance reports using reportlab"""
import os
from pathlib import Path
from datetime import datetime
from typing import Union, List, Tuple
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFGenerator:
    """Generate PDF reports from attendance data with tables and conclusions"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize PDF generator with output directory.
        
        Args:
            output_dir: Directory where PDFs will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_pdf_from_data(self, elements: List, filename: str) -> str:
        """
        Generate PDF from reportlab elements.
        
        Args:
            elements: List of reportlab elements (Paragraph, Table, Spacer, etc.)
            filename: Output filename (without .pdf extension)
            
        Returns:
            Path to generated PDF file
        """
        pdf_path = self.output_dir / f"{filename}.pdf"
        
        try:
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            doc.build(elements)
            print(f"✓ PDF generated: {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            print(f"✗ Error generating PDF: {e}")
            raise
    
    def create_report_a_pdf(self, report, filename: str = None) -> str:
        """
        Create PDF for Report A with table and conclusions.
        
        Args:
            report: AttendanceReportA object
            filename: Output filename (without .pdf extension)
            
        Returns:
            Path to generated PDF file
        """
        if filename is None:
            filename = f"report_a_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        elements = []
        
        # Title and timestamp
        elements.append(Paragraph("Attendance Report", self.styles['CustomTitle']))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            self.styles['Subtitle']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary section
        elements.append(Paragraph("Report Summary - Type A", self.styles['SectionHeading']))
        summary_data = [
            ["Metric", "Value"],
            ["Total Hours", str(report.total_hours or 0)],
            ["Total Days", str(report.total_days or 0)],
            ["Hourly Payment", f"${report.hour_payment or 0:.2f}"],
            ["Total Payment", f"${report.total_payment or 0:.2f}"],
        ]
        summary_table = self._create_table(summary_data, col_widths=[2.5*inch, 2.5*inch])
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Attendance table
        elements.append(Paragraph("Attendance Details", self.styles['SectionHeading']))
        table_data = [["Date", "Day", "Entry", "End", "Hours", "Notes"]]
        for row in report.rows:
            table_data.append([
                row.date or "-",
                row.day or "-",
                row.entry_time or "-",
                row.end_time or "-",
                str(row.sum) if row.sum else "-",
                row.note or "-"
            ])
        attendance_table = self._create_table(table_data, col_widths=[1.3*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
        elements.append(attendance_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Conclusion
        elements.append(self._create_conclusion_a(report))
        
        return self.generate_pdf_from_data(elements, filename)
    
    def create_report_b_pdf(self, report, filename: str = None) -> str:
        """
        Create PDF for Report B with table and conclusions.
        
        Args:
            report: AttendanceReportB object
            filename: Output filename (without .pdf extension)
            
        Returns:
            Path to generated PDF file
        """
        if filename is None:
            filename = f"report_b_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        elements = []
        
        # Title and timestamp
        elements.append(Paragraph("Attendance Report", self.styles['CustomTitle']))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}",
            self.styles['Subtitle']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary section
        elements.append(Paragraph("Report Summary - Type B", self.styles['SectionHeading']))
        summary_data = [
            ["Metric", "Value"],
            ["Total Hours", str(report.total_hours or 0)],
            ["Total Days", str(report.total_days or 0)],
            ["Total @ 100%", str(report.total_100 or 0)],
            ["Total @ 125%", str(report.total_125 or 0)],
            ["Total @ 150%", str(report.total_150 or 0)],
            ["Total Saturday", str(report.total_saturday or 0)],
            ["Bonus", f"${report.bonus or 0:.2f}"],
            ["Travel", f"${report.travel or 0:.2f}"],
        ]
        summary_table = self._create_table(summary_data, col_widths=[2.5*inch, 2.5*inch])
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Attendance table
        elements.append(Paragraph("Attendance Details", self.styles['SectionHeading']))
        table_data = [["Date", "Day", "Entry", "End", "Hours", "Location", "Break", "100%", "125%", "150%", "Sat"]]
        for row in report.rows:
            table_data.append([
                row.date or "-",
                row.day or "-",
                row.entry_time or "-",
                row.end_time or "-",
                str(row.sum) if row.sum else "-",
                row.location or "-",
                row.break_time or "-",
                str(row.col_100) if row.col_100 else "-",
                str(row.col_125) if row.col_125 else "-",
                str(row.col_150) if row.col_150 else "-",
                str(row.col_saturday) if row.col_saturday else "-",
            ])
        attendance_table = self._create_table(table_data, col_widths=[
            0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch,
            0.9*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.7*inch
        ])
        elements.append(attendance_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Conclusion
        elements.append(self._create_conclusion_b(report))
        
        return self.generate_pdf_from_data(elements, filename)
    
    def _create_table(self, data: List[List], col_widths: List = None) -> Table:
        """
        Create a styled table.
        
        Args:
            data: Table data as list of lists
            col_widths: Column widths
            
        Returns:
            Styled Table object
        """
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Body styling
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            
            # Right align numeric columns
            ('ALIGN', (-3, 0), (-1, -1), 'RIGHT'),
        ]))
        return table
    
    def _create_conclusion_a(self, report) -> Paragraph:
        """Create conclusion section for Report A"""
        total_payment_str = f"${report.total_payment:.2f}" if report.total_payment else "$0.00"
        
        conclusion_text = f"""
        <b>Conclusion</b><br/>
        <b>Report Type:</b> Attendance Report A<br/>
        <b>Total Work Hours:</b> {report.total_hours or 0} hours across {report.total_days or 0} days<br/>
        <b>Hourly Rate:</b> ${report.hour_payment or 0:.2f}/hour<br/>
        <b>Total Compensation:</b> {total_payment_str}<br/>
        <br/>
        This report summarizes the attendance and work hours for the specified period. 
        All times are based on OCR-extracted data and should be verified against original records.
        """
        
        return Paragraph(conclusion_text, self.styles['Normal'])
    
    def _create_conclusion_b(self, report) -> Paragraph:
        """Create conclusion section for Report B"""
        total_regular = (report.total_100 or 0)
        total_premium = (report.total_125 or 0) + (report.total_150 or 0)
        total_saturday = (report.total_saturday or 0)
        total_bonus = report.bonus or 0
        total_travel = report.travel or 0
        
        conclusion_text = f"""
        <b>Conclusion</b><br/>
        <b>Report Type:</b> Attendance Report B<br/>
        <b>Total Work Hours:</b> {report.total_hours or 0} hours across {report.total_days or 0} days<br/>
        <b>Regular Hours (100%):</b> {total_regular} hours<br/>
        <b>Premium Hours (125%-150%):</b> {total_premium} hours<br/>
        <b>Saturday Hours:</b> {total_saturday} hours<br/>
        <b>Bonus Amount:</b> ${total_bonus:.2f}<br/>
        <b>Travel Allowance:</b> ${total_travel:.2f}<br/>
        <br/>
        This report shows detailed attendance with rate multipliers and special work categories. 
        All times are based on OCR-extracted data and should be verified against original records.
        """
        
        return Paragraph(conclusion_text, self.styles['Normal'])
