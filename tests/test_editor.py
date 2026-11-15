import base64
import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from instruct_edit.editor import edit

FIXTURE = "tests/fixtures/sample.jpg"


def _make_b64_png(size=(1, 1)) -> str:
    buf = io.BytesIO()
    Image.new("RGB", size, color=(255, 255, 255)).save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def _mock_client_edit_ok():
    client = MagicMock()
    client.images.edit.return_value = MagicMock(
        data=[MagicMock(b64_json=_make_b64_png())]
    )
    return client


def test_edit_returns_pil_image():
    img = Image.open(FIXTURE)
    analysis = {"dalle_prompt": "golden-hour sunset sky, warm orange hues"}
    with patch("instruct_edit.editor.openai.OpenAI", return_value=_mock_client_edit_ok()):
        result = edit(analysis, img)
    assert isinstance(result, Image.Image)
    assert result.size == img.size


def test_edit_raises_on_missing_dalle_prompt():
    img = Image.open(FIXTURE)
    with pytest.raises(ValueError, match="dalle_prompt"):
        edit({}, img)


def test_edit_falls_back_on_bad_request():
    import openai as _openai

    img = Image.open(FIXTURE)
    analysis = {"dalle_prompt": "golden-hour sunset sky"}

    client = MagicMock()
    client.images.edit.side_effect = _openai.BadRequestError(
        message="content policy",
        response=MagicMock(status_code=400),
        body={},
    )
    client.images.generate.return_value = MagicMock(
        data=[MagicMock(b64_json=_make_b64_png())]
    )

    with patch("instruct_edit.editor.openai.OpenAI", return_value=client):
        result = edit(analysis, img)

    assert isinstance(result, Image.Image)
    client.images.generate.assert_called_once()


def test_edit_raises_runtime_on_api_error():
    import openai as _openai

    img = Image.open(FIXTURE)
    analysis = {"dalle_prompt": "golden-hour sunset sky"}

    client = MagicMock()
    client.images.edit.side_effect = _openai.APIConnectionError(request=MagicMock())

    with patch("instruct_edit.editor.openai.OpenAI", return_value=client):
        with pytest.raises(RuntimeError, match="OpenAI edit failed"):
            edit(analysis, img)
