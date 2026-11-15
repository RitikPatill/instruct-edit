import base64
import io

import openai
from openai import BadRequestError, OpenAIError
from PIL import Image

SUPPORTED_SIZES = [(256, 256), (512, 512), (1024, 1024)]


def _nearest_size(w: int, h: int) -> str:
    longest = max(w, h)
    for side, _ in SUPPORTED_SIZES:
        if side >= longest:
            return f"{side}x{side}"
    return "1024x1024"


def _to_rgba_png_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.convert("RGBA").save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _blank_mask_bytes(size: tuple) -> bytes:
    mask = Image.new("RGBA", size, (0, 0, 0, 0))
    buf = io.BytesIO()
    mask.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _generation_fallback(client, prompt: str, original_size: tuple) -> Image.Image:
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )
        img_bytes = base64.b64decode(response.data[0].b64_json)
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI edit failed: {e}") from e


def edit(analysis: dict, image: Image.Image) -> Image.Image:
    """
    Parameters
    ----------
    analysis : dict
        Output of analyzer.analyze() — must contain key 'dalle_prompt'.
    image : PIL.Image.Image
        The original image (any mode/size).

    Returns
    -------
    PIL.Image.Image  (RGB, same dimensions as input)
    """
    if "dalle_prompt" not in analysis:
        raise ValueError("analysis must contain 'dalle_prompt' key")

    prompt = analysis["dalle_prompt"]
    original_size = image.size  # (w, h)
    size_str = _nearest_size(*original_size)
    side = int(size_str.split("x")[0])
    resized = image.resize((side, side), Image.LANCZOS)

    image_bytes = _to_rgba_png_bytes(resized)
    mask_bytes = _blank_mask_bytes((side, side))

    client = openai.OpenAI()

    try:
        response = client.images.edit(
            model="dall-e-2",
            image=("image.png", io.BytesIO(image_bytes), "image/png"),
            mask=("mask.png", io.BytesIO(mask_bytes), "image/png"),
            prompt=prompt,
            n=1,
            size=size_str,
            response_format="b64_json",
        )
        img_bytes = base64.b64decode(response.data[0].b64_json)
        result = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except BadRequestError:
        result = _generation_fallback(client, prompt, original_size)
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI edit failed: {e}") from e

    return result.resize(original_size, Image.LANCZOS)
