import logging

from core.exceptions import OCRProcessingError


logger = logging.getLogger(__name__)


def pdf_to_images(pdf_path):
    """Convert PDF to images with error handling."""
    try:
        import fitz
        from PIL import Image
    except ImportError as exc:
        error_msg = 'fitz and PIL are required to convert PDF pages to images'
        logger.error(error_msg)
        raise OCRProcessingError(error_msg) from exc

    try:
        doc = fitz.open(pdf_path)
        images = []

        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            images.append(img)

        return images
    except Exception as e:
        error_msg = f"Failed to convert PDF to images: {e}"
        logger.error(error_msg)
        raise OCRProcessingError(error_msg) from e


def preprocess_image(image):
    """Preprocess image for OCR with error handling."""
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        error_msg = 'cv2 and numpy are required to preprocess images'
        logger.error(error_msg)
        raise OCRProcessingError(error_msg) from exc

    try:
        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
        return thresh
    except Exception as e:
        error_msg = f"Failed to preprocess image: {e}"
        logger.error(error_msg)
        raise OCRProcessingError(error_msg) from e


def extract_text_from_images(images):
    """Extract text from images using OCR with error handling."""
    try:
        import pytesseract
        import os
    except ImportError as exc:
        error_msg = 'pytesseract is required to extract text from images'
        logger.error(error_msg)
        raise OCRProcessingError(error_msg) from exc

    try:
        tesseract_path = os.environ.get("TESSERACT_CMD")
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    except Exception as e:
        logger.warning(f"Could not set tesseract path: {e}")

    extracted_text = ''

    try:
        for i, image in enumerate(images):
            processed = preprocess_image(image)
            config = '--oem 3 --psm 6'

            text = pytesseract.image_to_string(
                processed,
                lang='heb',
                config=config
            )

            extracted_text += f'--- Page {i + 1} ---\n'
            extracted_text += text + '\n\n'

        return extracted_text
    except Exception as e:
        error_msg = f"Failed to extract text from images: {e}"
        logger.error(error_msg)
        raise OCRProcessingError(error_msg) from e
