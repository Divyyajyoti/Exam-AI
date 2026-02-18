from __future__ import annotations
from fastapi import UploadFile
import os
from pathlib import Path

from pypdf import PdfReader

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None


async def extract_text_from_upload(file: UploadFile, data_dir: str) -> str:
    os.makedirs(data_dir, exist_ok=True)
    path = Path(data_dir) / file.filename

    content = await file.read()
    path.write_bytes(content)

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(str(path))

    if suffix in [".txt", ".md"]:
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix in [".png", ".jpg", ".jpeg"]:
        return _extract_image(str(path))

    # fallback
    return f"[Unsupported file type: {suffix}]"


def _extract_pdf(path: str) -> str:
    text_parts = []
    reader = PdfReader(path)
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            text_parts.append(t)
    return "\n\n".join(text_parts).strip()


def _extract_image(path: str) -> str:
    if Image is None or pytesseract is None:
        return (
            "[OCR unavailable]\n"
            "Install: pip install pillow pytesseract\n"
            "And install Tesseract OCR on Windows."
        )

    img = Image.open(path)
    txt = pytesseract.image_to_string(img)
    return (txt or "").strip()
