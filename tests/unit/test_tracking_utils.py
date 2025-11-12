"""
Unit tests for tracking utility functions

These are pure unit tests - they test individual functions in isolation
without any database or web framework dependencies.
"""

import pytest
from app.utils.tracking import generate_tracking_id, create_tracking_pixel


class TestGenerateTrackingId:
    """Test tracking ID generation function"""

    def test_returns_string(self):
        """Test that generate_tracking_id returns a string"""
        tracking_id = generate_tracking_id()
        assert isinstance(tracking_id, str)

    def test_correct_length(self):
        """Test that tracking ID has correct length (32 chars for UUID4 hex)"""
        tracking_id = generate_tracking_id()
        assert len(tracking_id) == 32

    def test_alphanumeric_only(self):
        """Test that tracking ID contains only alphanumeric characters"""
        tracking_id = generate_tracking_id()
        assert tracking_id.isalnum()

    def test_no_dashes(self):
        """Test that tracking ID doesn't contain dashes"""
        tracking_id = generate_tracking_id()
        assert '-' not in tracking_id

    def test_unique_ids(self):
        """Test that multiple calls generate unique IDs"""
        ids = [generate_tracking_id() for _ in range(100)]
        # All IDs should be unique
        assert len(set(ids)) == 100

    def test_lowercase_hex(self):
        """Test that tracking ID is lowercase hexadecimal"""
        tracking_id = generate_tracking_id()
        # Should be valid hex
        try:
            int(tracking_id, 16)
        except ValueError:
            pytest.fail("Tracking ID is not valid hexadecimal")


class TestCreateTrackingPixel:
    """Test tracking pixel generation function"""

    def test_returns_bytes(self):
        """Test that create_tracking_pixel returns bytes"""
        pixel = create_tracking_pixel()
        assert isinstance(pixel, bytes)

    def test_not_empty(self):
        """Test that pixel data is not empty"""
        pixel = create_tracking_pixel()
        assert len(pixel) > 0

    def test_png_signature(self):
        """Test that pixel starts with PNG signature"""
        pixel = create_tracking_pixel()
        # PNG files start with this signature
        png_signature = b'\x89PNG\r\n\x1a\n'
        assert pixel.startswith(png_signature)

    def test_png_end_marker(self):
        """Test that pixel ends with PNG end marker"""
        pixel = create_tracking_pixel()
        # PNG files end with IEND chunk
        assert pixel.endswith(b'IEND\xaeB`\x82')

    def test_consistent_output(self):
        """Test that function returns same pixel every time"""
        pixel1 = create_tracking_pixel()
        pixel2 = create_tracking_pixel()
        assert pixel1 == pixel2

    def test_small_size(self):
        """Test that pixel is small (should be under 100 bytes)"""
        pixel = create_tracking_pixel()
        # 1x1 transparent PNG should be very small
        assert len(pixel) < 100

    def test_exact_size(self):
        """Test that pixel is exactly the expected size"""
        pixel = create_tracking_pixel()
        # The specific implementation creates a 67-byte PNG
        assert len(pixel) == 67
