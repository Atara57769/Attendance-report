import re
from typing import Optional

from core.models.attendance_report_A_models import AttendanceReportA, AttendanceRowA
from processores.parse_processor import extract_total_days, extract_total_hours


class ProcessorA:


    def parse(self, raw_text: str) -> AttendanceReportA:
        """
        Parse raw OCR text from attendance report and extract data into AttendanceReportA model.
        
        Args:
            raw_text: String containing OCR-extracted text from PDF
            
        Returns:
            AttendanceReportA object with parsed data
        """
        report = AttendanceReportA()
        lines = raw_text.strip().split('\n')
        
        # Parse report-level data (total hours, total days, payments)
        report.total_hours = extract_total_hours(raw_text)
        report.total_days = extract_total_days(raw_text)
        report.hour_payment = self._extract_hour_payment(raw_text)
        report.total_payment = self._extract_total_payment(raw_text)
        
        # Parse attendance rows
        report.rows = self._parse_attendance_rows(lines)
        
        return report
    
    
    def _extract_hour_payment(self, text: str) -> Optional[float]:
        """Extract hourly payment rate from text."""
        match = re.search(r'hour(?:ly)?\s+(?:payment|rate|pay)\s*:?\s*([\d.]+)', text, re.IGNORECASE)
        return float(match.group(1)) if match else None
    
    def _extract_total_payment(self, text: str) -> Optional[float]:
        """Extract total payment amount from text."""
        match = re.search(r'total\s+(?:payment|pay)\s*:?\s*([\d.]+)', text, re.IGNORECASE)
        return float(match.group(1)) if match else None
    

    def _parse_row_line(self, line: str) -> Optional[AttendanceRowA]:
        if not line or len(line.strip()) < 5:
            return None
            
        pattern = r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})\s+([A-Za-z]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+([\d.]+)(?:\s+(.+))?'
        match = re.match(pattern, line.strip())
        
        if match:
            return AttendanceRowA(
                date=match.group(1),
                day=match.group(2),
                entry_time=match.group(3),
                end_time=match.group(4),
                sum=float(match.group(5)),
                note=match.group(6).strip() if match.group(6) else None
            )
        return None
    
    def _parse_attendance_rows(self, lines: list) -> list:
        """Parse individual attendance rows from text lines."""
        rows = []
        
        for line in lines:
            row = self._parse_row_line(line)
            if row:
                rows.append(row)
        
        return rows

    def apply_variation(self, model: AttendanceReportA) -> AttendanceReportA:
        pass

    def generate_pdf(self, model: AttendanceReportA, output_path: str) -> bool:
        pass