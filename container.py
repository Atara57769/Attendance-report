from factory.processor_factory import ProcessorFactory
from services.attendance_report_service import AttendanceReportService
from services.ocr_service import pdf_to_text

class AppBuilder:
    @staticmethod
    def build_attendance_service(output_dir: str) -> AttendanceReportService:
        factory = ProcessorFactory(output_dir=output_dir)
        
        return AttendanceReportService(
            factory=factory,
            ocr_service=pdf_to_text
        )