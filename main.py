
from services.attendance_report import process_attendance_report
from services.ocr_service import pdf_to_text

if __name__ == '__main__':
     process_attendance_report(r"D:\input_pdfs\n_r_5_n.pdf", "output.pdf")
     process_attendance_report(r"D:\input_pdfs\a_r_9.pdf", "output.pdf")
     process_attendance_report(r"D:\input_pdfs\a_r_25.pdf", "output.pdf")
     process_attendance_report(r"D:\input_pdfs\n_r_10_n.pdf", "output.pdf")
  
