import os

from repositories.ocr_reposiitory import extract_text_from_images, pdf_to_images


def pdf_to_text(pdf_path: str) -> str:
    """
    Main function: Convert PDF to text using Tesseract OCR.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        String containing extracted text from all pages
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Convert PDF to images
    images = pdf_to_images(pdf_path)
    
    # Extract text from images
    text = extract_text_from_images(images)

    text = clean_text(text)
    
    return text


def clean_text(text: str) -> str:
    """
    Basic cleaning for OCR output
    """
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # remove garbage lines
        if len(line) < 2:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)