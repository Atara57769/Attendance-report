import logging
import argparse
import sys
from container import AppBuilder

logger = logging.getLogger(__name__)

def run_cli():
    parser = argparse.ArgumentParser(description="Attendance Report CLI Tool")
    parser.add_argument("input", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", help="Path to the output directory", default=".")
    
    args = parser.parse_args()

    service = AppBuilder.build_attendance_service(output_dir=args.output)
    
    try:
        logger.info(f"Starting to process: {args.input}")
        service.process(args.input) 
        logger.info(f"Processed {args.input} successfully. Output saved to {args.output}")
    except Exception as e:
        logger.error(f"Error processing report: {e}")
        sys.exit(1)