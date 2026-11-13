import base64
import io
import json

import openai
from PIL import Image

SYSTEM_PROMPT = """You are an image-editing assistant. Respond with **only** a JSON object — no prose, no markdown. The object must have exactly these four string keys:
- `region_description` — the specific region of the image to modify
- `preserve_elements` — parts of the image that must remain unchanged
- `dalle_prompt` — a detailed, unambiguous DALL-E 3 inpainting prompt for the target region
- `confidence` — a one-sentence note on how clearly the region can be isolated"""

REQUIRED_KEYS = {"region_description", "preserve_elements", "dalle_prompt", "confidence"}


def _image_to_b64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.read()).decode()
    return f"data:image/jpeg;base64,{encoded}"


def analyze(image: Image.Image, instruction: str) -> dict:
    if not instruction.strip():
        raise ValueError("instruction must not be empty")

    image_url = _image_to_b64(image)

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": instruction},
                ],
            },
        ],
    )

    data = json.loads(response.choices[0].message.content)

    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"GPT-4o response missing keys: {missing}")

    return data
