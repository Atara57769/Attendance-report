from dataclasses import dataclass, field
from typing import List, Optional

from core.models.attendance_report import BaseAttendanceReport, BaseAttendanceRow



@dataclass
class AttendanceRowA(BaseAttendanceRow):
    note: Optional[str] = None

@dataclass
class AttendanceReportA(BaseAttendanceReport):
    rows: List[AttendanceRowA] = field(default_factory=list)
    hour_payment: Optional[float] = None
    total_payment: Optional[float] = None