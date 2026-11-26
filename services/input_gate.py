"""Input gate and zero-trust validation services for coffee bean images."""

import io
from pathlib import Path
from typing import Any
import warnings

from PIL import Image

from core.constants import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    MAX_IMAGE_PIXELS,
)
from core.exceptions import ImageValidationError


def validate_uploaded_file(uploaded_file: Any) -> Image.Image:
    """
    Validate uploaded file-like object from Streamlit or HTTP payload.
    Enforces real byte length, extension whitelist, magic bytes, decompression bomb shield,
    and returns a sanitized PIL Image re-encoded into an isolated memory buffer.
    """
    if uploaded_file is None:
        raise ImageValidationError("Berkas citra tidak boleh kosong.")

    # 1. Filename & extension validation
    filename = getattr(uploaded_file, "name", "")
    ext = Path(filename).suffix.lstrip(".").lower()
    if not ext or ext not in ALLOWED_EXTENSIONS:
        raise ImageValidationError(
            f"Ekstensi berkas '{ext}' tidak didukung. Pilihan valid: {ALLOWED_EXTENSIONS}"
        )

    # 2. Strict buffer length validation (never rely solely on client-reported size attribute)
    try:
        current_pos = uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
        raw_bytes = uploaded_file.read()
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(current_pos)
    except Exception as exc:
        raise ImageValidationError(f"Gagal membaca byte aliran berkas: {exc}")

    byte_len = len(raw_bytes)
    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if byte_len == 0:
        raise ImageValidationError("Berkas citra berukuran 0 byte (kosong).")
    if byte_len > max_bytes:
        raise ImageValidationError(
            f"Ukuran berkas ({byte_len / (1024 * 1024):.2f} MB) melebihi batas maksimal {MAX_FILE_SIZE_MB} MB."
        )

    # 3. Magic bytes, decompression bomb, and image format decoding
    try:
        stream = io.BytesIO(raw_bytes)
        # Catch decompression warnings and escalate to error locally (no global mutation)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(stream) as img:
                img_format = (img.format or "").lower()
                if img_format not in ["jpeg", "jpg", "png", "webp"]:
                    raise ImageValidationError(
                        f"Format citra '{img_format}' tidak diizinkan. Gunakan format JPG, PNG, atau WEBP."
                    )

                # Resolution ceiling guard (CWE-400)
                pixel_count = img.width * img.height
                if pixel_count > MAX_IMAGE_PIXELS:
                    raise ImageValidationError(
                        f"Resolusi citra ({img.width}x{img.height} = {pixel_count:,} px) melebihi batas 16 MP."
                    )

                # Force RGB conversion
                rgb_img = img.convert("RGB")

    except Image.DecompressionBombError:
        raise ImageValidationError(
            "Citra ditolak: Terdeteksi risiko dekompresi berbahaya (Decompression Bomb)."
        )
    except ImageValidationError:
        raise
    except Exception as exc:
        raise ImageValidationError(f"Format berkas rusak atau bukan citra valid: {exc}")

    # 4. Mandatory re-encoding into pristine buffer (strips EXIF, polyglot ZIP/appended bytes)
    reencoded_buf = io.BytesIO()
    rgb_img.save(reencoded_buf, format="PNG")
    reencoded_buf.seek(0)

    clean_img = Image.open(reencoded_buf)
    clean_img.load()
    return clean_img


def validate_pil_image(image: Any) -> Image.Image:
    """
    Defense-in-depth validator for PIL.Image objects before tensor preprocessing and inference.
    """
    if not isinstance(image, Image.Image):
        raise ImageValidationError(
            f"Input citra harus bertipe PIL.Image.Image, bukan {type(image).__name__}."
        )

    pixel_count = image.width * image.height
    if pixel_count > MAX_IMAGE_PIXELS:
        raise ImageValidationError(
            f"Resolusi citra ({image.width}x{image.height} = {pixel_count:,} px) melebihi batas 16 MP."
        )

    if image.mode != "RGB":
        image = image.convert("RGB")

    return image
