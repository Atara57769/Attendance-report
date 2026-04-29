from dataclasses import dataclass, field
from typing import List, Optional
from datetime import time
from datetime import date, time

@dataclass(frozen=True)
class AttendanceRow:
    date: Optional[date] = None
    day: Optional[str] = None
    entry_time: Optional[time] = None
    end_time: Optional[time] = None
    sum: Optional[float] = None
    
    note: Optional[str] = None
    location: Optional[str] = None 
    break_time: Optional[time] = None     
    col_100: Optional[float] = None  
    col_125: Optional[float] = None 
    col_150: Optional[float] = None     
    col_saturday: Optional[float] = None 


@dataclass(frozen=True)
class AttendanceReport:
    rows: List[AttendanceRow] = field(default_factory=list)
    
    total_hours: Optional[float] = None
    total_days: Optional[int] = None
    
    hour_payment: Optional[float] = None
    total_payment: Optional[float] = None
    total_100: Optional[float] = None
    total_125: Optional[float] = None
    total_150: Optional[float] = None
    total_saturday: Optional[float] = None
    bonus: Optional[float] = None        
    travel: Optional[float] = None