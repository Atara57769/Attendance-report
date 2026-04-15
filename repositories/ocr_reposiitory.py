import re

import fitz
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def pdf_to_images(pdf_path):
    images = []
    doc = fitz.open(pdf_path)

    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    return images


def extract_text_from_images(images):
    """
    Extract text from images using improved Tesseract OCR
    """

    try:
        extracted_text = ""

        for i, image in enumerate(images):

            # OCR config (better for tables)
            config = "--oem 3 --psm 6"

            # Extract text (Hebrew + English)
            text = pytesseract.image_to_string(
                image,
                lang="heb+eng",
                config=config
            )

            
            extracted_text += f"--- Page {i + 1} ---\n"
            extracted_text += text + "\n\n"

        return extracted_text

    except Exception as e:
        raise Exception(f"Error extracting text from images: {str(e)}")




