import os
import re
import logging

from repositories.ocr_reposiitory import extract_text_from_images, pdf_to_images

logger = logging.getLogger(__name__)

def pdf_to_text(pdf_path: str) -> str:
    logger.info(f"Converting PDF to text: {pdf_path}")
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    images = pdf_to_images(pdf_path)
    logger.debug(f"Extracted {len(images)} images from PDF")
    text = extract_text_from_images(images)
    text = clean_text(text)
    logger.info(f"Extracted text length: {len(text)}")

    return text


def clean_text(text: str) -> str:
    return text
    # lines = text.split("\n")
    # cleaned_lines = []

    # for line in lines:
    #     line = line.strip()

    #     if len(line) < 2 or "PS D:\\" in line or "projeect" in line:
    #         continue

    #     line = re.sub(r'(?<=\d),(?=\d)', '.', line)

    #     line = re.sub(r'\b(\d{2})(\d{2})\b', r'\1:\2', line)

    #     line = re.sub(r'[^\w\sא-ת\d\:\/\.\%\-\+]', ' ', line)

    #     line = re.sub(r'\s+', ' ', line).strip()

    #     if line:
    #         cleaned_lines.append(line)

    # return "\n".join(cleaned_lines)