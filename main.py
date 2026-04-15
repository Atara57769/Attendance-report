from processores.processor_a import ProcessorA
from processores.processor_b import ProcessorB
from services.ocr_service import pdf_to_text


def test_processor_a_with_pdf():
    """Test ProcessorA with real PDF using OCR"""
    print("=" * 50)
    print("Testing ProcessorA with Real PDF")
    print("=" * 50)
    
    pdf_path = r"D:\input_pdfs\a_r_25.pdf"
    
    try:
        # Extract text from PDF using OCR
        print(f"Extracting text from: {pdf_path}")
        raw_text = pdf_to_text(pdf_path)
        
        print("\nExtracted OCR text (first 500 chars):")
        print("-" * 50)
        print(raw_text[:500])
        print("-" * 50)
        
        # Parse the extracted text
        processor_a = ProcessorA()
        report_a = processor_a.parse(raw_text)
        
        print(f"\nParsed Report A:")
        print(f"Total Hours: {report_a.total_hours}")
        print(f"Total Days: {report_a.total_days}")
        print(f"Hour Payment: {report_a.hour_payment}")
        print(f"Total Payment: {report_a.total_payment}")
        print(f"\nParsed Rows ({len(report_a.rows)}):")
        for i, row in enumerate(report_a.rows, 1):
            print(f"  {i}. {row.date} {row.day}: {row.entry_time}-{row.end_time} ({row.sum}h) - Note: {row.note}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_processor_a_sample():
    """Test ProcessorA with sample data"""
    print("=" * 50)
    print("Testing ProcessorA with Sample Data")
    print("=" * 50)
    
    # Sample OCR text for Report A
    sample_text_a = """
    Attendance Report A
    Total Hours: 40.5
    Total Days: 5
    Hourly Payment: 25.00
    Total Payment: 1012.50
    
    01/04/2024 Monday 09:00 17:30 8.5
    02/04/2024 Tuesday 09:00 17:30 8.5 Worked early
    03/04/2024 Wednesday 09:00 17:30 8.5
    04/04/2024 Thursday 09:00 17:30 8.5
    05/04/2024 Friday 09:00 17:00 7.5 Left early
    """
    
    processor_a = ProcessorA()
    report_a = processor_a.parse(sample_text_a)
    
    print(f"Total Hours: {report_a.total_hours}")
    print(f"Total Days: {report_a.total_days}")
    print(f"Hour Payment: {report_a.hour_payment}")
    print(f"Total Payment: {report_a.total_payment}")
    print(f"\nParsed Rows ({len(report_a.rows)}):")
    for row in report_a.rows:
        print(f"  {row.date} {row.day}: {row.entry_time}-{row.end_time} ({row.sum}h) - Note: {row.note}")
    print()


if __name__ == '__main__':
    # Test with real PDF
    test_processor_a_with_pdf()
    
    # T
