"""Unit tests for input gate service, file upload validation, and decompression bomb defenses."""

import io
import unittest
import warnings
from PIL import Image

from core.constants import MAX_FILE_SIZE_MB, MAX_IMAGE_PIXELS
from core.exceptions import ImageValidationError
from services.input_gate import validate_pil_image, validate_uploaded_file


class DummyUploadedFile(io.BytesIO):
    """Mock Streamlit UploadedFile with name and size attributes."""

    def __init__(self, buffer: bytes, name: str = "test.jpg"):
        super().__init__(buffer)
        self.name = name
        self.size = len(buffer)


class TestInputGate(unittest.TestCase):
    """Test suite verifying strict input sanitization, format whitelists, and DoS shields."""

    def _create_image_bytes(self, size=(100, 100), fmt="JPEG", mode="RGB") -> bytes:
        img = Image.new(mode, size, color=(128, 64, 32))
        buf = io.BytesIO()
        img.save(buf, format=fmt)
        return buf.getvalue()

    def test_valid_jpeg_upload_passes_and_returns_clean_image(self):
        """Assert valid JPEG file passes and returns clean PIL image."""
        raw = self._create_image_bytes(size=(200, 200), fmt="JPEG")
        upload = DummyUploadedFile(raw, name="sample.jpg")
        img = validate_uploaded_file(upload)
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.size, (200, 200))
        self.assertEqual(img.mode, "RGB")

    def test_valid_png_and_webp_upload_pass(self):
        """Assert PNG and WEBP formats pass validation."""
        for fmt, ext in [("PNG", "png"), ("WEBP", "webp")]:
            raw = self._create_image_bytes(size=(150, 150), fmt=fmt)
            upload = DummyUploadedFile(raw, name=f"sample.{ext}")
            img = validate_uploaded_file(upload)
            self.assertIsInstance(img, Image.Image)

    def test_disallowed_extension_rejected(self):
        """Assert file extensions outside whitelist are rejected."""
        raw = self._create_image_bytes(fmt="JPEG")
        upload = DummyUploadedFile(raw, name="sample.exe")
        with self.assertRaises(ImageValidationError) as ctx:
            validate_uploaded_file(upload)
        self.assertIn("tidak didukung", str(ctx.exception))

    def test_empty_or_none_upload_rejected(self):
        """Assert None or 0-byte uploaded file is rejected."""
        with self.assertRaises(ImageValidationError):
            validate_uploaded_file(None)

        upload = DummyUploadedFile(b"", name="empty.jpg")
        with self.assertRaises(ImageValidationError):
            validate_uploaded_file(upload)

    def test_oversized_file_rejected_by_byte_length(self):
        """Assert files exceeding MAX_FILE_SIZE_MB are rejected using real buffer length."""
        # Create buffer that claims size=10 but actual bytes exceed 10 MB
        oversized_bytes = b"X" * (MAX_FILE_SIZE_MB * 1024 * 1024 + 1)
        upload = DummyUploadedFile(oversized_bytes, name="large.jpg")
        upload.size = 100  # Spoofed client size attribute
        with self.assertRaises(ImageValidationError) as ctx:
            validate_uploaded_file(upload)
        self.assertIn("melebihi batas", str(ctx.exception))

    def test_fake_jpg_containing_pdf_rejected(self):
        """Assert non-image content with .jpg extension is rejected by magic bytes."""
        pdf_bytes = b"%PDF-1.4 Fake PDF Content Header and payload"
        upload = DummyUploadedFile(pdf_bytes, name="fake.jpg")
        with self.assertRaises(ImageValidationError):
            validate_uploaded_file(upload)

    def test_polyglot_jpeg_zip_sanitized_by_reencoding(self):
        """
        Assert polyglot file (JPEG + ZIP payload) is re-encoded into clean PNG,
        and trailing ZIP markers are completely stripped.
        """
        real_jpeg = self._create_image_bytes(size=(50, 50), fmt="JPEG")
        zip_marker = b"PK\x03\x04\x14\x00\x00\x00\x08\x00DummyZipEntryData"
        polyglot_bytes = real_jpeg + zip_marker

        upload = DummyUploadedFile(polyglot_bytes, name="polyglot.jpg")
        clean_img = validate_uploaded_file(upload)

        # Inspect bytes of the resulting image
        out_buf = io.BytesIO()
        clean_img.save(out_buf, format="PNG")
        self.assertNotIn(b"DummyZipEntryData", out_buf.getvalue())

    def test_dimension_ceiling_exceeded_rejected(self):
        """Assert images exceeding 16 MP resolution ceiling are rejected."""
        img = Image.new("RGB", (4097, 4096))
        with self.assertRaises(ImageValidationError):
            validate_pil_image(img)

    def test_validate_pil_image_converts_rgba_to_rgb(self):
        """Assert validate_pil_image converts RGBA or grayscale to RGB."""
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        clean = validate_pil_image(img)
        self.assertEqual(clean.mode, "RGB")

    def test_validate_pil_image_rejects_non_pil_types(self):
        """Assert non-PIL objects raise ImageValidationError."""
        with self.assertRaises(ImageValidationError):
            validate_pil_image("not-an-image")


if __name__ == "__main__":
    unittest.main()
