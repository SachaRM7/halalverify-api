from __future__ import annotations

import re
from pathlib import Path


def extract_barcode_from_text(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r'(\d{8,14})', text)
    return match.group(1) if match else None


def extract_barcode_from_image_path(image_path: str | Path) -> str | None:
    path = Path(image_path)

    try:
        from pyzbar.pyzbar import decode  # type: ignore
        from PIL import Image  # type: ignore

        codes = decode(Image.open(path))
        for code in codes:
            value = code.data.decode('utf-8').strip()
            if value.isdigit() and 8 <= len(value) <= 14:
                return value
    except Exception:
        pass

    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore

        text = pytesseract.image_to_string(Image.open(path))
        return extract_barcode_from_text(text)
    except Exception:
        return None
