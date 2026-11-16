import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from instruct_edit.app import app

client = TestClient(app)

FIXED_ANALYSIS = {
    "region_description": "the sky",
    "preserve_elements": "buildings, trees",
    "dalle_prompt": "a dramatic sunset sky with orange and pink hues",
    "confidence": "High confidence — sky is clearly separated from foreground.",
}


def _make_png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1, 1)).save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def test_index_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert "InstructEdit" in response.text


def test_analyze_ok():
    png = _make_png_bytes()
    with patch("instruct_edit.app.analyze", return_value=FIXED_ANALYSIS):
        response = client.post(
            "/analyze",
            files={"image": ("test.png", png, "image/png")},
            data={"instruction": "make it sunset"},
        )
    assert response.status_code == 200
    body = response.json()
    for key in ("region_description", "preserve_elements", "dalle_prompt", "confidence"):
        assert key in body


def test_analyze_empty_instruction():
    png = _make_png_bytes()
    with patch("instruct_edit.app.analyze", side_effect=ValueError("instruction must not be empty")):
        response = client.post(
            "/analyze",
            files={"image": ("test.png", png, "image/png")},
            data={"instruction": "   "},
        )
    assert response.status_code == 422


def test_edit_ok():
    png = _make_png_bytes()
    edited_img = Image.new("RGB", (1, 1))
    with patch("instruct_edit.app.analyze", return_value=FIXED_ANALYSIS), \
         patch("instruct_edit.app.edit", return_value=edited_img):
        response = client.post(
            "/edit",
            files={"image": ("test.png", png, "image/png")},
            data={"instruction": "make it sunset"},
        )
    assert response.status_code == 200
    body = response.json()
    assert "analysis" in body
    assert "edited_image" in body
    assert body["edited_image"].startswith("data:image/png;base64,")


def test_edit_runtime_error():
    png = _make_png_bytes()
    with patch("instruct_edit.app.analyze", return_value=FIXED_ANALYSIS), \
         patch("instruct_edit.app.edit", side_effect=RuntimeError("OpenAI edit failed")):
        response = client.post(
            "/edit",
            files={"image": ("test.png", png, "image/png")},
            data={"instruction": "make it sunset"},
        )
    assert response.status_code == 502


def test_index_returns_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_index_contains_required_elements():
    r = client.get("/")
    body = r.text
    assert 'id="drop-zone"' in body
    assert 'id="instruction"' in body
    assert 'id="submit-btn"' in body
    assert 'id="reasoning-block"' in body
    assert 'id="result-section"' in body
