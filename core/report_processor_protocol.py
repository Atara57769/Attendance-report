from typing import Protocol, TypeVar

from core.models.attendance_report import BaseAttendanceReport


T = TypeVar('T', bound=BaseAttendanceReport)

class ReportProcessor(Protocol[T]):

    def parse(self, raw_text: str) -> T:
        ...

    def apply_variation(self, model: T) -> T:
        ...

    def generate_pdf(self, model: T) -> bool:
        ...