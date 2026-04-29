
import logging
from services.attendance_report_service import AttendanceReportService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting attendance report processing")
    
    # Create service with DI (no container)
    service = AttendanceReportService()
    
    try:
        service.process(r"D:\input_pdfs\n_r_5_n.pdf")
        logger.info("Processed n_r_5_n.pdf successfully")
        service.process(r"D:\input_pdfs\a_r_9.pdf")
        logger.info("Processed a_r_9.pdf successfully")
        service.process(r"D:\input_pdfs\a_r_25.pdf")
        logger.info("Processed a_r_25.pdf successfully")
        service.process(r"D:\input_pdfs\n_r_10_n.pdf")
        logger.info("Processed n_r_10_n.pdf successfully")
        logger.info("All reports processed successfully")
    except Exception as e:
        logger.error(f"Error processing reports: {e}")
        raise
  
