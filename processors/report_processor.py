from typing import Optional
from core.models.attendance_report_models import AttendanceReport
from parse.base_parser import BaseParsingService
from pdf_render.base_render import BasePDFService
from variation.validating_strategy_decorator import ValidatingStrategyDecorator


class ReportProcessor:

    def __init__(
        self,
        parser: BaseParsingService,
        variation_service: ValidatingStrategyDecorator,
        pdf_service: BasePDFService,
    ) -> None:
        self.parser = parser
        self.variation = variation_service
        self.pdf = pdf_service

    def parse(self, raw_text: str) -> AttendanceReport:
        return self.parser.parse(raw_text)

    def apply_variation(self, report: AttendanceReport, seed: Optional[int] = None) -> AttendanceReport:
        return self.variation.apply(report, seed)

    def generate_pdf(self, report: AttendanceReport) -> str:
        return self.pdf.generate(report)

