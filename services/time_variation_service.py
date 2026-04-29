from datetime import datetime, timedelta
import random
from typing import Tuple, Optional


class TimeVariationService:

    @staticmethod
    def calculate_hours(entry_time: str, exit_time: str) -> float:
        try:
            entry_dt = datetime.strptime(entry_time, "%H:%M")
            exit_dt = datetime.strptime(exit_time, "%H:%M")

            if exit_dt <= entry_dt:
                return 0.0

            return round((exit_dt - entry_dt).total_seconds() / 3600, 2)

        except ValueError:
            return 0.0

    @staticmethod
    def apply_variation(entry_time: str, exit_time: str) -> Tuple[str, str, float]:
        try:
            entry_dt = datetime.strptime(entry_time, "%H:%M")
            exit_dt = datetime.strptime(exit_time, "%H:%M")

            entry_dt += timedelta(minutes=random.randint(0, 20))
            exit_dt += timedelta(minutes=random.randint(0, 20))

            if exit_dt <= entry_dt:
                exit_dt = entry_dt + timedelta(minutes=1)

            hours = (exit_dt - entry_dt).total_seconds() / 3600

            return (
                entry_dt.strftime("%H:%M"),
                exit_dt.strftime("%H:%M"),
                round(hours, 2)
            )

        except ValueError:
            return None, None, 0.0

    @staticmethod
    def calculate_total_hours(rows) -> float:
        return round(sum(r.sum for r in rows if r.sum > 0), 2)

    @staticmethod
    def calculate_total_days(rows) -> int:
        return len(rows)

    @staticmethod
    def apply_break_variation(break_time: str) -> Optional[str]:
        try:
            if not break_time or break_time == "00:00":
                return break_time

            dt = datetime.strptime(break_time, "%H:%M")
            dt += timedelta(minutes=random.randint(0, 15))
            return dt.strftime("%H:%M")

        except ValueError:
            return None

    @staticmethod
    def calculate_hours_with_break(entry_time, exit_time, break_time) -> float:
        try:
            entry_dt = datetime.strptime(entry_time, "%H:%M")
            exit_dt = datetime.strptime(exit_time, "%H:%M")

            if exit_dt <= entry_dt:
                return 0.0

            total_hours = (exit_dt - entry_dt).total_seconds() / 3600

            if break_time and break_time != "00:00":
                b = datetime.strptime(break_time, "%H:%M")
                break_minutes = b.hour * 60 + b.minute

                max_minutes = (exit_dt - entry_dt).total_seconds() / 60
                if break_minutes >= max_minutes:
                    break_minutes = 0

                total_hours -= break_minutes / 60

            return round(max(0, total_hours), 2)

        except ValueError:
            return 0.0