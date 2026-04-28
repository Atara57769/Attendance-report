from dataclasses import dataclass, field
from typing import List, Optional

from core.models.attendance_report import BaseAttendanceRow, BaseAttendanceReport


@dataclass(frozen=True)
class AttendanceRow(BaseAttendanceRow):
    # From AttendanceRowA
    note: Optional[str] = None
    # From AttendanceRowB
    location: Optional[str] = None 
    break_time: Optional[str] = None     
    col_100: Optional[float] = None  
    col_125: Optional[float] = None 
    col_150: Optional[float] = None     
    col_saturday: Optional[float] = None 

@dataclass(frozen=True)
class AttendanceReport(BaseAttendanceReport):
    rows: List[AttendanceRow] = field(default_factory=list)
    # From AttendanceReportA
    hour_payment: Optional[float] = None
    total_payment: Optional[float] = None
    # From AttendanceReportB
    total_100: Optional[float] = None
    total_125: Optional[float] = None
    total_150: Optional[float] = None
    total_saturday: Optional[float] = None
    bonus: Optional[float] = None        
    travel: Optional[float] = None