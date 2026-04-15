from dataclasses import dataclass, field
from typing import List, Optional

from core.models.attendance_report import BaseAttendanceReport, BaseAttendanceRow


@dataclass
class AttendanceRowB(BaseAttendanceRow):
    location: Optional[str] = None 
    break_time: Optional[str] = None     
    col_100: Optional[float] = None  
    col_125: Optional[float] = None 
    col_150: Optional[float] = None     
    col_saturday: Optional[float] = None 

@dataclass
class AttendanceReportB(BaseAttendanceReport):
    rows: List[AttendanceRowB] = field(default_factory=list)  
    total_100: Optional[float] = None
    total_125: Optional[float] = None
    total_150: Optional[float] = None
    total_saturday: Optional[float] = None
    bonus: Optional[float] = None        
    travel: Optional[float] = None