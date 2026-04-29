
import logging
from services.attendance_report import process_attendance_report
from services.ocr_service import pdf_to_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('attendance_report.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting attendance report processing")
    try:
        process_attendance_report(r"D:\input_pdfs\n_r_5_n.pdf")
        logger.info("Processed n_r_5_n.pdf successfully")
        process_attendance_report(r"D:\input_pdfs\a_r_9.pdf")
        logger.info("Processed a_r_9.pdf successfully")
        process_attendance_report(r"D:\input_pdfs\a_r_25.pdf")
        logger.info("Processed a_r_25.pdf successfully")
        process_attendance_report(r"D:\input_pdfs\n_r_10_n.pdf")
        logger.info("Processed n_r_10_n.pdf successfully")
        logger.info("All reports processed successfully")
    except Exception as e:
        logger.error(f"Error processing reports: {e}")
        raise
  
