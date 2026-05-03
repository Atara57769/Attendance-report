import random
from datetime import time
from core.models.attendance_report_models import AttendanceRow
from variation.variation_a import VariationA

rng = random.Random(42)
row = AttendanceRow(entry_time=time(9, 0), end_time=time(17, 0), break_time=time(0, 30))
v = VariationA()
new_row = v._build_row(row, time(9, 0), time(17, 0), rng)
print("New sum:", new_row.sum)
