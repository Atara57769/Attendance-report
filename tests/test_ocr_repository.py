import sys
import types

import pytest

from core.exceptions import OCRProcessingError
from repositories import ocr_reposiitory as repo


def test_pdf_to_images_happy_path(monkeypatch):
    class FakePixmap:
        width = 10
        height = 20
        samples = b"pixels"

    class FakePage:
        def get_pixmap(self, matrix):
            assert matrix == ("matrix", 2, 2)
            return FakePixmap()

    class FakeFitz(types.SimpleNamespace):
        @staticmethod
        def open(path):
            assert path == "report.pdf"
            return [FakePage(), FakePage()]

        @staticmethod
        def Matrix(x, y):
            return ("matrix", x, y)

    class FakeImageModule(types.SimpleNamespace):
        @staticmethod
        def frombytes(mode, size, samples):
            return {"mode": mode, "size": size, "samples": samples}

    monkeypatch.setitem(sys.modules, "fitz", FakeFitz())
    monkeypatch.setitem(sys.modules, "PIL", types.SimpleNamespace(Image=FakeImageModule()))

    images = repo.pdf_to_images("report.pdf")

    assert images == [
        {"mode": "RGB", "size": [10, 20], "samples": b"pixels"},
        {"mode": "RGB", "size": [10, 20], "samples": b"pixels"},
    ]


def test_pdf_to_images_import_error(monkeypatch):
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fitz":
            raise ImportError("missing fitz")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(OCRProcessingError, match="fitz and PIL are required"):
        repo.pdf_to_images("report.pdf")


def test_pdf_to_images_runtime_error(monkeypatch):
    class FakeFitz(types.SimpleNamespace):
        @staticmethod
        def open(path):
            raise RuntimeError("boom")

    class FakeImageModule(types.SimpleNamespace):
        pass

    monkeypatch.setitem(sys.modules, "fitz", FakeFitz())
    monkeypatch.setitem(sys.modules, "PIL", types.SimpleNamespace(Image=FakeImageModule()))

    with pytest.raises(OCRProcessingError, match="Failed to convert PDF to images: boom"):
        repo.pdf_to_images("report.pdf")


def test_preprocess_image_happy_path(monkeypatch):
    calls = []

    class FakeCv2(types.SimpleNamespace):
        COLOR_BGR2GRAY = "gray"
        THRESH_BINARY = "binary"

        @staticmethod
        def cvtColor(img, color):
            calls.append(("cvtColor", img, color))
            return "gray-image"

        @staticmethod
        def GaussianBlur(img, kernel, sigma):
            calls.append(("GaussianBlur", img, kernel, sigma))
            return "blurred-image"

        @staticmethod
        def threshold(img, thresh, maxval, kind):
            calls.append(("threshold", img, thresh, maxval, kind))
            return None, "threshold-image"

    class FakeNumpy(types.SimpleNamespace):
        @staticmethod
        def array(image):
            calls.append(("array", image))
            return "np-image"

    monkeypatch.setitem(sys.modules, "cv2", FakeCv2())
    monkeypatch.setitem(sys.modules, "numpy", FakeNumpy())

    result = repo.preprocess_image("raw-image")

    assert result == "threshold-image"
    assert calls == [
        ("array", "raw-image"),
        ("cvtColor", "np-image", "gray"),
        ("GaussianBlur", "gray-image", (3, 3), 0),
        ("threshold", "blurred-image", 150, 255, "binary"),
    ]


def test_preprocess_image_import_error(monkeypatch):
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "cv2":
            raise ImportError("missing cv2")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(OCRProcessingError, match="cv2 and numpy are required"):
        repo.preprocess_image("raw-image")


def test_preprocess_image_runtime_error(monkeypatch):
    class FakeCv2(types.SimpleNamespace):
        COLOR_BGR2GRAY = "gray"
        THRESH_BINARY = "binary"

        @staticmethod
        def cvtColor(img, color):
            raise RuntimeError("bad image")

    class FakeNumpy(types.SimpleNamespace):
        @staticmethod
        def array(image):
            return "np-image"

    monkeypatch.setitem(sys.modules, "cv2", FakeCv2())
    monkeypatch.setitem(sys.modules, "numpy", FakeNumpy())

    with pytest.raises(OCRProcessingError, match="Failed to preprocess image: bad image"):
        repo.preprocess_image("raw-image")


def test_extract_text_from_images_happy_path(monkeypatch):
    preprocess_calls = []

    def fake_preprocess(image):
        preprocess_calls.append(image)
        return f"processed-{image}"

    fake_pytesseract = types.SimpleNamespace(
        pytesseract=types.SimpleNamespace(tesseract_cmd=None),
        image_to_string=lambda image, lang, config: f"text:{image}:{lang}:{config}",
    )

    monkeypatch.setattr(repo, "preprocess_image", fake_preprocess)
    monkeypatch.setitem(sys.modules, "pytesseract", fake_pytesseract)
    monkeypatch.setenv("TESSERACT_CMD", "C:\\tesseract.exe")

    text = repo.extract_text_from_images(["img1", "img2"])

    assert preprocess_calls == ["img1", "img2"]
    assert fake_pytesseract.pytesseract.tesseract_cmd == "C:\\tesseract.exe"
    assert text == (
        "--- Page 1 ---\ntext:processed-img1:heb:--oem 3 --psm 6\n\n"
        "--- Page 2 ---\ntext:processed-img2:heb:--oem 3 --psm 6\n\n"
    )


def test_extract_text_from_images_import_error(monkeypatch):
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pytesseract":
            raise ImportError("missing pytesseract")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(OCRProcessingError, match="pytesseract is required"):
        repo.extract_text_from_images(["img1"])


def test_extract_text_from_images_ocr_error(monkeypatch):
    monkeypatch.setattr(repo, "preprocess_image", lambda image: image)
    fake_pytesseract = types.SimpleNamespace(
        pytesseract=types.SimpleNamespace(tesseract_cmd=None),
        image_to_string=lambda image, lang, config: (_ for _ in ()).throw(RuntimeError("ocr failed")),
    )
    monkeypatch.setitem(sys.modules, "pytesseract", fake_pytesseract)

    with pytest.raises(OCRProcessingError, match="Failed to extract text from images: ocr failed"):
        repo.extract_text_from_images(["img1"])
