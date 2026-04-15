

from core.models.attendance_report_A_models import AttendanceReportA
from core.models.attendance_report_B_models import AttendanceReportB


def get_processor(raw_text):
    if "150%" in raw_text and "100%" in raw_text:
        return AttendanceReportA()
    return AttendanceReportB()