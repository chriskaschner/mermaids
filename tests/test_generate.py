"""Tests for OpenAI image generation pipeline (mocked API)."""

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


def _mock_response():
    """Build a mock OpenAI images.generate response with b64_json data."""
    image_obj = MagicMock()
    image_obj.b64_json = TINY_PNG_B64
    resp = MagicMock()
    resp.data = [image_obj]
    return resp


# -------------------------------------------------------
# config.py
# -------------------------------------------------------


def test_config_paths_are_pathlib():
    """All path constants in config.py are Path objects."""
    from mermaids.pipeline.config import (
        FRONTEND_SVG_DIR,
        GENERATED_PNG_DIR,
        GENERATED_SVG_DIR,
    )

    assert isinstance(GENERATED_PNG_DIR, Path)
    assert isinstance(GENERATED_SVG_DIR, Path)
    assert isinstance(FRONTEND_SVG_DIR, Path)


# -------------------------------------------------------
# prompts.py
# -------------------------------------------------------


def test_coloring_prompts_are_bw_outline():
    """COLORING_BASE_PROMPT contains 'black and white' and 'outline' keywords."""
    from mermaids.pipeline.prompts import COLORING_BASE_PROMPT

    lower = COLORING_BASE_PROMPT.lower()
    assert "black and white" in lower
    assert "outline" in lower


# -------------------------------------------------------
# generate.py -- generate_image
# -------------------------------------------------------


class TestGenerateImage:
    """Tests for the generate_image function."""

    def test_generate_image_calls_api(self, tmp_path):
        """generate_image() calls client.images.generate with correct params
        and returns decoded bytes written to output_path."""
        from mermaids.pipeline.generate import generate_image

        output = tmp_path / "test.png"
        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_response()

        with patch("mermaids.pipeline.generate._get_client", return_value=mock_client):
            result = generate_image("test prompt", output)

        assert result == output
        assert output.exists()
        # Verify the API was called
        mock_client.images.generate.assert_called_once()
        call_kwargs = mock_client.images.generate.call_args
        assert call_kwargs.kwargs.get("model") == "gpt-image-1" or (
            call_kwargs.args and "gpt-image-1" in str(call_kwargs)
        )
        assert call_kwargs.kwargs.get("prompt") == "test prompt"

    def test_generate_image_skips_existing(self, tmp_path):
        """generate_image() returns early without API call when output file
        already exists."""
        from mermaids.pipeline.generate import generate_image

        output = tmp_path / "existing.png"
        output.write_bytes(b"already here")

        mock_client = MagicMock()

        with patch("mermaids.pipeline.generate._get_client", return_value=mock_client):
            result = generate_image("test prompt", output)

        assert result == output
        # API should NOT have been called
        mock_client.images.generate.assert_not_called()

    def test_generate_image_retries_on_rate_limit(self, tmp_path):
        """generate_image() retries up to 3 times on RateLimitError with
        increasing delays."""
        import openai

        from mermaids.pipeline.generate import generate_image

        output = tmp_path / "retry.png"
        mock_client = MagicMock()

        # Fail twice with RateLimitError, then succeed
        rate_err = openai.RateLimitError(
            message="rate limit",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )
        mock_client.images.generate.side_effect = [
            rate_err,
            rate_err,
            _mock_response(),
        ]

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch("mermaids.pipeline.generate.time.sleep"),
        ):
            result = generate_image("test prompt", output)

        assert result == output
        assert output.exists()
        assert mock_client.images.generate.call_count == 3

    def test_generate_image_retries_on_api_error(self, tmp_path):
        """generate_image() retries up to 3 times on APIError."""
        import openai

        from mermaids.pipeline.generate import generate_image

        output = tmp_path / "api_err.png"
        mock_client = MagicMock()

        api_err = openai.APIError(
            message="server error",
            request=MagicMock(),
            body=None,
        )
        mock_client.images.generate.side_effect = [
            api_err,
            _mock_response(),
        ]

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch("mermaids.pipeline.generate.time.sleep"),
        ):
            result = generate_image("test prompt", output)

        assert result == output
        assert mock_client.images.generate.call_count == 2

    def test_generate_image_raises_after_max_retries(self, tmp_path):
        """generate_image() raises after exhausting retry attempts."""
        import openai

        from mermaids.pipeline.generate import generate_image

        output = tmp_path / "fail.png"
        mock_client = MagicMock()

        rate_err = openai.RateLimitError(
            message="rate limit",
            response=MagicMock(status_code=429, headers={}),
            body=None,
        )
        mock_client.images.generate.side_effect = rate_err

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch("mermaids.pipeline.generate.time.sleep"),
            pytest.raises(openai.RateLimitError),
        ):
            generate_image("test prompt", output)

        # Should have tried 1 + 3 retries = 4 calls, or 3 total (depending on impl)
        # At minimum, more than 1 attempt
        assert mock_client.images.generate.call_count > 1


class TestGenerateColoringPages:
    """Tests for generate_coloring_pages function."""

    def test_generate_coloring_pages_produces_all_nine(self, tmp_path):
        """generate_coloring_pages() calls generate_image for each of the 9
        coloring page definitions."""
        from mermaids.pipeline.generate import generate_coloring_pages

        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_response()

        with (
            patch("mermaids.pipeline.generate._get_client", return_value=mock_client),
            patch(
                "mermaids.pipeline.config.GENERATED_PNG_DIR",
                tmp_path / "generated" / "png",
            ),
        ):
            results = generate_coloring_pages()

        assert len(results) == 9
        # All should be Path objects
        for r in results:
            assert isinstance(r, Path)

    def test_coloring_page_prompts_have_distinct_styles(self):
        """All 9 COLORING_PAGES entries have unique IDs and distinct prompt_detail."""
        from mermaids.pipeline.prompts import COLORING_PAGES

        assert len(COLORING_PAGES) == 9, f"Expected 9 coloring pages, got {len(COLORING_PAGES)}"

        ids = [p["id"] for p in COLORING_PAGES]
        assert len(ids) == len(set(ids)), "All COLORING_PAGES IDs must be unique"

        prompts = [p["prompt_detail"] for p in COLORING_PAGES]
        assert len(prompts) == len(set(prompts)), "All COLORING_PAGES prompt_detail values must be unique"


class TestGenerateDressupCharacters:
    """Tests for generate_dressup_characters function."""

    def test_generate_dressup_characters_produces_nine(self, tmp_path):
        """generate_dressup_characters() produces 9 character PNGs."""
        from mermaids.pipeline.generate import generate_dressup_characters

        mock_client = MagicMock()
        mock_client.images.generate.return_value = _mock_response()

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
        assert names == {f"mermaid-{i}" for i in range(1, 10)}
