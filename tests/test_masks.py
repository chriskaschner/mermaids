"""Tests for mask creation and dress-up variant generation via edit API (mocked)."""

import base64
import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image


def _make_tiny_png_b64() -> str:
    """Create a base64-encoded 1x1 white PNG for mock API responses."""
    img = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


TINY_PNG_B64 = _make_tiny_png_b64()


def _mock_generate_response():
    """Build a mock OpenAI images.generate response with b64_json data."""
    image_obj = MagicMock()
    image_obj.b64_json = TINY_PNG_B64
    resp = MagicMock()
    resp.data = [image_obj]
    return resp


def _mock_edit_response():
    """Build a mock OpenAI images.edit response with b64_json data."""
    image_obj = MagicMock()
    image_obj.b64_json = TINY_PNG_B64
    resp = MagicMock()
    resp.data = [image_obj]
    return resp


@pytest.fixture
def base_mermaid_png(tmp_path) -> Path:
    """Create a simple test PNG simulating a base mermaid image."""
    img = Image.new("RGBA", (1024, 1024), (200, 150, 200, 255))
    path = tmp_path / "dressup" / "base" / "mermaid-base.png"
    path.parent.mkdir(parents=True)
    img.save(path)
    return path


# -------------------------------------------------------
# Mask creation tests
# -------------------------------------------------------


class TestCreateRegionMask:
    """Tests for create_region_mask()."""

    def test_create_region_mask_correct_size(self):
        """create_region_mask() returns a PNG with the same pixel dimensions as specified."""
        from mermaids.pipeline.edit import create_region_mask

        mask_bytes = create_region_mask((1024, 1024), (200, 500, 824, 1024))
        img = Image.open(io.BytesIO(mask_bytes))
        assert img.size == (1024, 1024)

    def test_create_region_mask_transparent_region(self):
        """Pixels inside the region bbox are transparent (alpha=0),
        pixels outside are opaque (alpha=255)."""
        from mermaids.pipeline.edit import create_region_mask

        mask_bytes = create_region_mask((100, 100), (20, 30, 80, 70))
        img = Image.open(io.BytesIO(mask_bytes))

        # Check pixel inside the region (transparent)
        _, _, _, alpha_inside = img.getpixel((50, 50))
        assert alpha_inside == 0, f"Expected alpha=0 inside region, got {alpha_inside}"

        # Check pixel outside the region (opaque)
        _, _, _, alpha_outside = img.getpixel((5, 5))
        assert alpha_outside == 255, f"Expected alpha=255 outside region, got {alpha_outside}"

        # Check another outside pixel (bottom-left corner)
        _, _, _, alpha_outside2 = img.getpixel((5, 95))
        assert alpha_outside2 == 255, f"Expected alpha=255 outside region, got {alpha_outside2}"

    def test_create_region_mask_rgba_format(self):
        """Output mask is RGBA PNG format."""
        from mermaids.pipeline.edit import create_region_mask

        mask_bytes = create_region_mask((256, 256), (50, 50, 200, 200))
        img = Image.open(io.BytesIO(mask_bytes))
        assert img.mode == "RGBA"


# -------------------------------------------------------
# Base mermaid generation tests
# -------------------------------------------------------


class TestGenerateBaseMermaid:
    """Tests for generate_base_mermaid()."""

    def test_generate_base_mermaid_calls_api(self, tmp_path):
        """generate_base_mermaid() calls images.generate with dress-up prompt (mocked)."""
        from mermaids.pipeline.edit import generate_base_mermaid

        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_generate_response()

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch(
                "mermaids.pipeline.config.GENERATED_PNG_DIR",
                tmp_path / "generated" / "png",
            ),
        ):
            result = generate_base_mermaid()

        assert isinstance(result, Path)
        assert result.exists()
        mock_client.images.generate.assert_called_once()

    def test_generate_base_mermaid_skips_existing(self, tmp_path):
        """generate_base_mermaid() skips if base PNG already exists."""
        from mermaids.pipeline.edit import generate_base_mermaid

        # Pre-create the base image
        base_dir = tmp_path / "generated" / "png" / "dressup" / "base"
        base_dir.mkdir(parents=True)
        base_file = base_dir / "mermaid-base.png"
        base_file.write_bytes(b"existing")

        mock_client = MagicMock()

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch(
                "mermaids.pipeline.config.GENERATED_PNG_DIR",
                tmp_path / "generated" / "png",
            ),
        ):
            result = generate_base_mermaid()

        assert result == base_file
        mock_client.images.generate.assert_not_called()


# -------------------------------------------------------
# Edit region tests
# -------------------------------------------------------


class TestEditRegion:
    """Tests for edit_region()."""

    def test_edit_region_calls_edit_api(self, tmp_path):
        """edit_region() calls images.edit with base image, mask, and prompt (mocked)."""
        from mermaids.pipeline.edit import edit_region

        # Create a base image file
        base_img = Image.new("RGBA", (64, 64), (200, 150, 200, 255))
        base_path = tmp_path / "base.png"
        base_img.save(base_path)

        mask_bytes = b"\x89PNG\r\n"  # Minimal bytes, won't be validated by mock
        # Create proper mask bytes
        from mermaids.pipeline.edit import create_region_mask

        mask_bytes = create_region_mask((64, 64), (10, 10, 50, 50))

        output = tmp_path / "variant.png"

        mock_client = MagicMock()
        mock_client.images.edit.return_value = _mock_edit_response()

        with patch("mermaids.pipeline.edit._get_client", return_value=mock_client):
            result = edit_region(base_path, mask_bytes, "test prompt", output)

        assert result == output
        assert output.exists()
        mock_client.images.edit.assert_called_once()


# -------------------------------------------------------
# Full variant generation tests
# -------------------------------------------------------


class TestGenerateDressupVariants:
    """Tests for generate_dressup_variants()."""

    def test_generate_dressup_variants_produces_all_nine(self, tmp_path):
        """generate_dressup_variants() produces 3 tails + 3 hair + 3 accessories = 9 variant PNGs."""
        from mermaids.pipeline.edit import generate_dressup_variants

        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_generate_response()
        mock_client.images.edit.return_value = _mock_edit_response()

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch("mermaids.pipeline.edit._get_client", return_value=mock_client),
            patch(
                "mermaids.pipeline.config.GENERATED_PNG_DIR",
                tmp_path / "generated" / "png",
            ),
        ):
            results = generate_dressup_variants()

        assert len(results) == 9
        # All should be Path objects
        for r in results:
            assert isinstance(r, Path)

        # Check expected variant IDs in filenames
        names = {r.stem for r in results}
        expected = {
            "tail-1", "tail-2", "tail-3",
            "hair-1", "hair-2", "hair-3",
            "acc-1", "acc-2", "acc-3",
        }
        assert names == expected
