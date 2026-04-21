import re


def pdf_to_images(pdf_path):
    images = []
    try:
        import fitz
        from PIL import Image
    except ImportError as exc:
        raise ImportError('fitz and PIL are required to convert PDF pages to images') from exc

    doc = fitz.open(pdf_path)

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        images.append(img)

    return images


def preprocess_image(image):
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise ImportError('cv2 and numpy are required to preprocess images') from exc

    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
    return thresh


def extract_text_from_images(images):
    try:
        import pytesseract
    except ImportError as exc:
        raise ImportError('pytesseract is required to extract text from images') from exc

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    extracted_text = ''

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
