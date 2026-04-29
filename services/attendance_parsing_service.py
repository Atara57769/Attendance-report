import re
from typing import Optional, List


class AttendanceParsingService:

    @staticmethod
    def normalize_line(line: str) -> str:
        line = line.replace("|", " ")
        return re.sub(r"\s+", " ", line).strip()

    @staticmethod
    def extract_times(line: str) -> List[str]:
        raw_times = re.findall(r'\d{1,4}[:.]?\d{0,2}', line)
        times = []

        for t in raw_times:
            if ":" in t or "." in t:
                t = t.replace(".", ":")
                parts = t.split(":")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    h, m = int(parts[0]), int(parts[1])
                    if h < 24 and m < 60:
                        times.append(f"{h:02d}:{m:02d}")

            elif t.isdigit():
                val = int(t)
                if 100 <= val <= 2359:
                    h, m = val // 100, val % 100
                    if h < 24 and m < 60:
                        times.append(f"{h:02d}:{m:02d}")

        return times

    @staticmethod
    def extract_numbers(line: str) -> List[float]:
        nums = re.findall(r'\d+(?:\.\d+)?', line)

        def fix(val_str):
            val = float(val_str)
            if val >= 100 and "." not in val_str:
                return val / 100.0
            return val

        return [fix(n) for n in nums]

    @staticmethod
    def extract_day(line: str) -> Optional[str]:
        match = re.search(r'(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)', line)
        return match.group(1) if match else None

    @staticmethod
    def extract_date(line: str) -> str:
        match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]?\d{0,4}', line)
        return match.group(0) if match else ""

    @staticmethod
    def clean_text(line: str) -> str:
        line = re.sub(r'\d+(?:[/:.]\d+)?', '', line)
        return re.sub(r'[^\w\sא-ת]', '', line).strip()

    @staticmethod
    def extract_total_hours(text: str) -> Optional[float]:
        match = re.search(r'([\d,]+\.\d+).*?שעות|שעות.*?([\d,]+\.\d+)', text, re.DOTALL)
        if match:
            val = match.group(1) or match.group(2)
            return float(val.replace(',', ''))
        return None

    @staticmethod
    def extract_total_days(text: str) -> Optional[int]:
        match = re.search(r'(\d+).*?ימים|ימים.*?(\d+)', text)
        return int(match.group(1) or match.group(2)) if match else None

    @staticmethod
    def extract_hour_payment(text: str) -> Optional[float]:
        match = re.search(r'([\d,]+\.\d+).*?שעה|שעה.*?([\d,]+\.\d+)', text, re.DOTALL)
        if match:
            val = match.group(1) or match.group(2)
            return float(val.replace(',', ''))
        return None

    @staticmethod
    def extract_total_payment(text: str) -> Optional[float]:
        match = re.search(r'([\d,]+\.\d+).*?תשלום|תשלום.*?([\d,]+\.\d+)', text, re.DOTALL)
        if match:
            val = match.group(1) or match.group(2)
            return float(val.replace(',', ''))
        return None