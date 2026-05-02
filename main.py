import logging
import argparse
import sys
from services.attendance_report_service import AttendanceReportService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Attendance Report CLI Tool")
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", help="Path to the output directory", default=".")
    
    args = parser.parse_args()

    service = AttendanceReportService(output_dir=args.output)
    
    try:
        logger.info(f"Starting to process: {args.input}")
        service.process(args.input) 
        logger.info(f"Processed {args.input} successfully. Output saved to {args.output}")
    except Exception as e:
        logger.error(f"Error processing report: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()