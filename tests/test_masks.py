"""Tests for mask creation, region definitions, and character generation (mocked API)."""

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


# -------------------------------------------------------
# Mask creation tests
# -------------------------------------------------------


class TestCreateRegionMask:
    """Tests for create_region_mask()."""

    def test_create_region_mask_correct_size(self):
        """create_region_mask() returns a PNG with the specified dimensions."""
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

        _, _, _, alpha_inside = img.getpixel((50, 50))
        assert alpha_inside == 0, f"Expected alpha=0 inside region, got {alpha_inside}"

        _, _, _, alpha_outside = img.getpixel((5, 5))
        assert alpha_outside == 255, f"Expected alpha=255 outside region, got {alpha_outside}"

    def test_create_region_mask_rgba_format(self):
        """Output mask is RGBA PNG format."""
        from mermaids.pipeline.edit import create_region_mask

        mask_bytes = create_region_mask((256, 256), (50, 50, 200, 200))
        img = Image.open(io.BytesIO(mask_bytes))
        assert img.mode == "RGBA"


# -------------------------------------------------------
# Region definition tests
# -------------------------------------------------------


class TestRegions:
    """Tests for REGIONS dict: 4 non-overlapping bounding boxes."""

    def test_regions_has_four_categories(self):
        """REGIONS has exactly 4 keys: tail, hair, eyes, acc."""
        from mermaids.pipeline.edit import REGIONS

        assert set(REGIONS.keys()) == {"tail", "hair", "eyes", "acc"}

    def _bboxes_overlap(self, a: tuple, b: tuple) -> bool:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
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
                    f"REGIONS['{k1}'] overlaps REGIONS['{k2}']"
                )

    def test_hair_tail_no_vertical_overlap(self):
        """Hair and tail regions have zero vertical overlap (DEBT-03 fix)."""
        from mermaids.pipeline.edit import REGIONS

        _, hair_y1, _, hair_y2 = REGIONS["hair"]
        _, tail_y1, _, tail_y2 = REGIONS["tail"]
        assert hair_y2 <= tail_y1 or tail_y2 <= hair_y1


# -------------------------------------------------------
# Character prompt tests (replaces DRESSUP_VARIANTS tests)
# -------------------------------------------------------


class TestDressupCharacterPrompts:
    """Tests for DRESSUP_CHARACTERS: 9 diverse mermaid characters."""

    def test_has_nine_characters(self):
        """DRESSUP_CHARACTERS has exactly 9 entries."""
        from mermaids.pipeline.prompts import DRESSUP_CHARACTERS

        assert len(DRESSUP_CHARACTERS) == 9

    def test_each_has_id_and_prompt(self):
        """Each character has 'id' and 'prompt_detail' keys."""
        from mermaids.pipeline.prompts import DRESSUP_CHARACTERS

        for char in DRESSUP_CHARACTERS:
            assert "id" in char, f"Missing 'id' in character: {char}"
            assert "prompt_detail" in char, f"Missing 'prompt_detail' in character: {char}"

    def test_ids_are_mermaid_1_through_9(self):
        """Character IDs are mermaid-1 through mermaid-9."""
        from mermaids.pipeline.prompts import DRESSUP_CHARACTERS

        ids = {c["id"] for c in DRESSUP_CHARACTERS}
        expected = {f"mermaid-{i}" for i in range(1, 10)}
        assert ids == expected

    def test_base_prompt_is_full_color(self):
        """DRESSUP_BASE_PROMPT specifies full color (not black-and-white)."""
        from mermaids.pipeline.prompts import DRESSUP_BASE_PROMPT

        lower = DRESSUP_BASE_PROMPT.lower()
        assert "full color" in lower or "color" in lower
        assert "black and white" not in lower


# -------------------------------------------------------
# Character generation tests (mocked API)
# -------------------------------------------------------


class TestGenerateDressupCharacters:
    """Tests for generate_dressup_characters()."""

    def test_generates_nine_characters(self, tmp_path):
        """generate_dressup_characters() produces 9 character PNGs."""
        from mermaids.pipeline.generate import generate_dressup_characters

        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_generate_response()

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch(
                "mermaids.pipeline.config.GENERATED_PNG_DIR",
                tmp_path / "generated" / "png",
            ),
        ):
            results = generate_dressup_characters()

        assert len(results) == 9
        for r in results:
            assert isinstance(r, Path)

        names = {r.stem for r in results}
        expected = {f"mermaid-{i}" for i in range(1, 10)}
        assert names == expected


# -------------------------------------------------------
# Edit region tests (still valid -- edit API still exists)
# -------------------------------------------------------


class TestEditRegion:
    """Tests for edit_region()."""

    def test_edit_region_calls_edit_api(self, tmp_path):
        """edit_region() calls images.edit with base image, mask, and prompt."""
        from mermaids.pipeline.edit import create_region_mask, edit_region

        base_img = Image.new("RGBA", (64, 64), (200, 150, 200, 255))
        base_path = tmp_path / "base.png"
        base_img.save(base_path)

        mask_bytes = create_region_mask((64, 64), (10, 10, 50, 50))
        output = tmp_path / "variant.png"

        mock_client = MagicMock()
        mock_edit_response = MagicMock()
        mock_edit_response.data = [MagicMock(b64_json=TINY_PNG_B64)]
        mock_client.images.edit.return_value = mock_edit_response

        with patch("mermaids.pipeline.edit._get_client", return_value=mock_client):
            result = edit_region(base_path, mask_bytes, "test prompt", output)

        assert result == output
        assert output.exists()
        mock_client.images.edit.assert_called_once()
