from unittest.mock import patch, MagicMock
import json
import pytest
from PIL import Image
from instruct_edit.analyzer import analyze

FIXTURE = "tests/fixtures/sample.jpg"

FAKE_RESPONSE = {
    "region_description": "sky in the upper half",
    "preserve_elements": "buildings, foreground",
    "dalle_prompt": "golden-hour sunset sky, warm orange hues, photorealistic",
    "confidence": "high",
}


def _mock_openai(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=json.dumps(FAKE_RESPONSE)))]
    )
    return mock_client


def test_analyze_returns_all_keys(monkeypatch):
    img = Image.open(FIXTURE)
    with patch("instruct_edit.analyzer.openai.OpenAI", return_value=_mock_openai(monkeypatch)):
        result = analyze(img, "make it sunset")
    assert set(result.keys()) == {"region_description", "preserve_elements", "dalle_prompt", "confidence"}
    assert all(isinstance(v, str) for v in result.values())


def test_analyze_raises_on_empty_instruction():
    img = Image.open(FIXTURE)
    with pytest.raises(ValueError, match="instruction"):
        analyze(img, "   ")


def test_analyze_raises_on_missing_keys(monkeypatch):
    img = Image.open(FIXTURE)
    incomplete = {"region_description": "sky"}
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=json.dumps(incomplete)))]
    )
    with patch("instruct_edit.analyzer.openai.OpenAI", return_value=mock_client):
        with pytest.raises(ValueError, match="missing keys"):
            analyze(img, "make it sunset")
