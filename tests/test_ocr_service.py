import pytest

from core.exceptions import OCRProcessingError
from services import ocr_service


def test_pdf_to_text_happy_path(monkeypatch):
    monkeypatch.setattr(ocr_service.os.path, "exists", lambda path: True)
    monkeypatch.setattr(ocr_service, "pdf_to_images", lambda path: ["img1", "img2"])
    monkeypatch.setattr(ocr_service, "extract_text_from_images", lambda images: "raw text")
    monkeypatch.setattr(ocr_service, "clean_text", lambda text: "clean text")

    result = ocr_service.pdf_to_text("report.pdf")

    assert result == "clean text"


def test_pdf_to_text_missing_file(monkeypatch):
    monkeypatch.setattr(ocr_service.os.path, "exists", lambda path: False)

    with pytest.raises(FileNotFoundError, match="PDF file not found: report.pdf"):
        ocr_service.pdf_to_text("report.pdf")


def test_pdf_to_text_pdf_to_images_failure(monkeypatch):
    monkeypatch.setattr(ocr_service.os.path, "exists", lambda path: True)
    monkeypatch.setattr(
        ocr_service,
        "pdf_to_images",
        lambda path: (_ for _ in ()).throw(RuntimeError("render failed")),
    )

    with pytest.raises(OCRProcessingError, match="Failed to convert PDF to images: render failed"):
        ocr_service.pdf_to_text("report.pdf")


def test_pdf_to_text_extract_failure(monkeypatch):
    monkeypatch.setattr(ocr_service.os.path, "exists", lambda path: True)
    monkeypatch.setattr(ocr_service, "pdf_to_images", lambda path: ["img1"])
    monkeypatch.setattr(
        ocr_service,
        "extract_text_from_images",
        lambda images: (_ for _ in ()).throw(RuntimeError("ocr failed")),
    )

    with pytest.raises(OCRProcessingError, match="Failed to extract text from images: ocr failed"):
        ocr_service.pdf_to_text("report.pdf")


def test_clean_text_returns_input():
    assert ocr_service.clean_text("some text") == "some text"
