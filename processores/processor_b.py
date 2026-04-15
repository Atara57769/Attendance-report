
import re
from typing import Optional

from core.models.attendance_report_B_models import AttendanceReportB, AttendanceRowB
from processores.parse_processor import extract_total_days, extract_total_hours


class ProcessorB:
   
    def parse(self, raw_text: str) -> AttendanceReportB:
        """
        Parse raw OCR text from attendance report B and extract data into AttendanceReportB model.
        
        Args:
            raw_text: String containing OCR-extracted text from PDF
            
        Returns:
            AttendanceReportB object with parsed data
        """
        report = AttendanceReportB()
        lines = raw_text.strip().split('\n')
        
        # Parse report-level data
        report.total_hours = extract_total_hours(raw_text)
        report.total_days = extract_total_days(raw_text)
        report.total_100 = self._extract_value(raw_text, r'total\s+100\s*:?\s*([\d.]+)')
        report.total_125 = self._extract_value(raw_text, r'total\s+125\s*:?\s*([\d.]+)')
        report.total_150 = self._extract_value(raw_text, r'total\s+150\s*:?\s*([\d.]+)')
        report.total_saturday = self._extract_value(raw_text, r'total\s+(?:saturday|sat)\s*:?\s*([\d.]+)')
        report.bonus = self._extract_value(raw_text, r'bonus\s*:?\s*([\d.]+)')
        report.travel = self._extract_value(raw_text, r'travel\s*:?\s*([\d.]+)')
        
        # Parse attendance rows
        report.rows = self._parse_attendance_rows(lines)
        
        return report
    
    
    
    def _extract_value(self, text: str, pattern: str) -> Optional[float]:
        """Helper to extract float value using regex pattern."""
        match = re.search(pattern, text, re.IGNORECASE)
        return float(match.group(1)) if match else None
    
    def _parse_attendance_rows(self, lines: list) -> list:
        """Parse individual attendance rows from text lines."""
        rows = []
        
        for line in lines:
            row = self._parse_row_line(line)
            if row:
                rows.append(row)
        
        return rows
    
    def _parse_row_line(self, line: str) -> Optional[AttendanceRowB]:
        """
        Parse a single attendance row line for Report B.
        Expected format variations:
        - DATE DAY ENTRY_TIME END_TIME HOURS LOCATION BREAK_TIME COL_100 COL_125 COL_150 COL_SAT [NOTE]
        """
        if not line or len(line.strip()) < 5:
            return None
        
        # Pattern to match: date, day, entry time, end time, hours, and optional additional fields
        pattern = r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})\s+([A-Za-z]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+([\d.]+)(?:\s+(\S+?))?(?:\s+(\d{1,2}:\d{2}))?(?:\s+([\d.]+))?(?:\s+([\d.]+))?(?:\s+([\d.]+))?(?:\s+([\d.]+))?'
        match = re.match(pattern, line.strip())
        
        if match:
            return AttendanceRowB(
                date=match.group(1),
                day=match.group(2),
                entry_time=match.group(3),
                end_time=match.group(4),
                sum=float(match.group(5)),
                location=match.group(6) if match.group(6) else None,
                break_time=match.group(7) if match.group(7) else None,
                col_100=float(match.group(8)) if match.group(8) else None,
                col_125=float(match.group(9)) if match.group(9) else None,
                col_150=float(match.group(10)) if match.group(10) else None,
                col_saturday=float(match.group(11)) if match.group(11) else None,
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
    

    def apply_variation(self, model: AttendanceReportB) -> AttendanceReportB:
        pass

    def generate_pdf(self, model: AttendanceReportB, output_path: str) -> bool:
        pass