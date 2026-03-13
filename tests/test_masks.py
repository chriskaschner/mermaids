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
# Region definition tests (new for 4-category design)
# -------------------------------------------------------


class TestRegions:
    """Tests for REGIONS dict: 4 non-overlapping bounding boxes."""

    def test_regions_has_four_categories(self):
        """REGIONS has exactly 4 keys: tail, hair, eyes, acc."""
        from mermaids.pipeline.edit import REGIONS

        assert set(REGIONS.keys()) == {"tail", "hair", "eyes", "acc"}, (
            f"Expected exactly 4 keys (tail, hair, eyes, acc), got {set(REGIONS.keys())}"
        )

    def test_eyes_region_exists(self):
        """REGIONS has an 'eyes' key."""
        from mermaids.pipeline.edit import REGIONS

        assert "eyes" in REGIONS, "REGIONS must contain 'eyes' key"

    def _bboxes_overlap(self, a: tuple, b: tuple) -> bool:
        """Return True if two (x1,y1,x2,y2) bboxes overlap."""
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        # No overlap if one is fully left, right, above, or below the other
        if ax2 <= bx1 or bx2 <= ax1:
            return False
        if ay2 <= by1 or by2 <= ay1:
            return False
        return True

    def test_regions_do_not_overlap(self):
        """No pair of REGIONS bboxes intersect."""
        from mermaids.pipeline.edit import REGIONS

        keys = list(REGIONS.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                assert not self._bboxes_overlap(REGIONS[k1], REGIONS[k2]), (
                    f"REGIONS['{k1}'] {REGIONS[k1]} overlaps REGIONS['{k2}'] {REGIONS[k2]}"
                )

    def test_hair_tail_no_vertical_overlap(self):
        """Hair and tail regions have zero vertical overlap (DEBT-03 fix)."""
        from mermaids.pipeline.edit import REGIONS

        _, hair_y1, _, hair_y2 = REGIONS["hair"]
        _, tail_y1, _, tail_y2 = REGIONS["tail"]

        # Hair must end (y2) before tail begins (y1), or tail ends before hair begins
        no_overlap = hair_y2 <= tail_y1 or tail_y2 <= hair_y1
        assert no_overlap, (
            f"Hair region y={hair_y1}-{hair_y2} overlaps tail region y={tail_y1}-{tail_y2} "
            f"(DEBT-03: hair y2={hair_y2} must be <= tail y1={tail_y1})"
        )

    def test_eyes_region_in_face_area(self):
        """Eyes region fits within the face/center-upper area (y < 600)."""
        from mermaids.pipeline.edit import REGIONS

        _, eyes_y1, _, eyes_y2 = REGIONS["eyes"]
        assert eyes_y2 <= 600, (
            f"Eyes region y2={eyes_y2} should be within face area (< 600)"
        )
        assert eyes_y1 >= 0, "Eyes region y1 must be non-negative"


# -------------------------------------------------------
# Prompts tests (new for 4-category design)
# -------------------------------------------------------


class TestDressupVariantsPrompts:
    """Tests for DRESSUP_VARIANTS: 4 categories with 3 variants each."""

    def test_dressup_variants_has_four_categories(self):
        """DRESSUP_VARIANTS has exactly 4 keys: tails, hair, eyes, accessories."""
        from mermaids.pipeline.prompts import DRESSUP_VARIANTS

        assert set(DRESSUP_VARIANTS.keys()) == {"tails", "hair", "eyes", "accessories"}, (
            f"Expected 4 categories, got {set(DRESSUP_VARIANTS.keys())}"
        )

    def test_dressup_variants_has_twelve_total(self):
        """DRESSUP_VARIANTS has 12 total variants (3 per category)."""
        from mermaids.pipeline.prompts import DRESSUP_VARIANTS

        total = sum(len(v) for v in DRESSUP_VARIANTS.values())
        assert total == 12, f"Expected 12 total variants, got {total}"

    def test_dressup_variants_eyes_category(self):
        """DRESSUP_VARIANTS has 'eyes' category with 3 variants."""
        from mermaids.pipeline.prompts import DRESSUP_VARIANTS

        assert "eyes" in DRESSUP_VARIANTS, "DRESSUP_VARIANTS must contain 'eyes'"
        eyes = DRESSUP_VARIANTS["eyes"]
        assert len(eyes) == 3, f"Expected 3 eye variants, got {len(eyes)}"
        ids = {v["id"] for v in eyes}
        assert ids == {"eye-1", "eye-2", "eye-3"}, (
            f"Expected eye IDs eye-1, eye-2, eye-3, got {ids}"
        )

    def test_dressup_variants_each_category_has_three(self):
        """Each category in DRESSUP_VARIANTS has exactly 3 variants."""
        from mermaids.pipeline.prompts import DRESSUP_VARIANTS

        for category, variants in DRESSUP_VARIANTS.items():
            assert len(variants) == 3, (
                f"Category '{category}' has {len(variants)} variants, expected 3"
            )


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
                "mermaids.pipeline.edit.GENERATED_PNG_DIR",
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
                "mermaids.pipeline.edit.GENERATED_PNG_DIR",
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
# Full variant generation tests (updated for 12 variants)
# -------------------------------------------------------


class TestGenerateDressupVariants:
    """Tests for generate_dressup_variants()."""

    def test_generate_dressup_variants_produces_twelve(self, tmp_path):
        """generate_dressup_variants() produces 3 tails + 3 hair + 3 eyes + 3 accessories = 12 variant PNGs."""
        from mermaids.pipeline.edit import generate_dressup_variants

        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_generate_response()
        mock_client.images.edit.return_value = _mock_edit_response()

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch("mermaids.pipeline.edit._get_client", return_value=mock_client),
            patch(
                "mermaids.pipeline.edit.GENERATED_PNG_DIR",
                tmp_path / "generated" / "png",
            ),
        ):
            results = generate_dressup_variants()

        assert len(results) == 12, f"Expected 12 variants, got {len(results)}"
        # All should be Path objects
        for r in results:
            assert isinstance(r, Path)

        # Check expected variant IDs in filenames
        names = {r.stem for r in results}
        expected = {
            "tail-1", "tail-2", "tail-3",
            "hair-1", "hair-2", "hair-3",
            "eye-1", "eye-2", "eye-3",
            "acc-1", "acc-2", "acc-3",
        }
        assert names == expected, (
            f"Expected variant IDs {expected}, got {names}"
        )
