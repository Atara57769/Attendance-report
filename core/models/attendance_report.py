from dataclasses import dataclass, field
from typing import List, Optional
@dataclass(frozen=True)

class BaseAttendanceRow:
    date: Optional[str] = None
    day: Optional[str] = None
    entry_time: Optional[str] = None
    end_time: Optional[str] = None
    sum: Optional[float] = None

@dataclass(frozen=True)
class BaseAttendanceReport:
    total_hours: Optional[float] = None
    total_days: Optional[int] = None