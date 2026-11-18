# InstructEdit — LLM-Guided Image Editing Pipeline

> Describe an edit in plain English; an LLM reasons about the image and rewrites the prompt before DALL-E applies it.

<!-- TODO: replace with a 5-10 second demo gif. Record with ScreenToGif on
     Windows or peek on macOS. Save to docs/demo.gif and update path here. -->
![demo](docs/demo.gif)

## What it is

InstructEdit is a locally-runnable web app that lets you upload any image, type a free-form instruction ("make it sunset", "remove the car", "turn the wall blue"), and receive an edited result — without fine-tuning or a local GPU.

The core idea is a two-stage LLM chain. First, GPT-4o receives the image and your raw instruction and returns a structured JSON object: what region to change, what to preserve, and an optimised inpainting prompt. Second, that refined prompt is sent to DALL-E 2's edit endpoint (with a DALL-E 3 generation fallback). The browser renders the original and edited images side by side, with the pipeline's reasoning JSON available for inspection.

## Quickstart

```bash
git clone https://github.com/RitikPatill/instruct-edit.git
cd instruct-edit

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your OpenAI key
cp .env.example .env
# Open .env and set OPENAI_API_KEY=sk-...

# Start the server
PYTHONPATH=src uvicorn instruct_edit.app:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

Drag an image onto the upload panel (JPEG or PNG, under 4 MB), type an instruction in the text box, and click **Edit**. The page sends a single `POST /edit` request; while it processes, the reasoning JSON returned by GPT-4o is shown in a collapsible panel above the before/after image pair.

To call the API directly:

```bash
curl -X POST http://localhost:8000/edit \
  -F "image=@demo/samples/city_street.jpg" \
  -F "instruction=make the sky a dramatic sunset"
```

The response is JSON with two keys: `analysis` (the GPT-4o reasoning object) and `edited_image` (a base64 PNG data URL).

## Architecture

```
User: image + instruction
        |
        v
  POST /analyze
  GPT-4o Vision
        |
        v
  Structured JSON
  { region, preserve, dalle_prompt, confidence }
        |
        v
  POST /edit
  DALL-E 2 edit endpoint  ──(BadRequestError)──> DALL-E 3 generate (fallback)
        |
        v
  Edited image (PNG)
        |
        v
  Before / after comparison in browser
```

## Project structure

```
instruct-edit/
├── src/instruct_edit/
│   ├── analyzer.py     # Stage 1: GPT-4o vision call → structured JSON
│   ├── editor.py       # Stage 2: DALL-E 2 edit, DALL-E 3 fallback
│   └── app.py          # FastAPI app — GET /, POST /analyze, POST /edit
├── templates/
│   └── index.html      # Jinja2 template, full drag-and-drop UI
├── static/
│   ├── style.css       # dark theme, responsive before/after grid
│   └── app.js          # vanilla JS: upload, fetch, render results
├── tests/              # pytest suite for analyzer, editor, and app
├── demo/samples/       # three CC0 reference images
├── .env.example        # required environment variables
└── requirements.txt    # pinned Python dependencies
```

## Roadmap

- [ ] Mask-drawing UI so users can restrict edits to a painted region instead of the whole image
- [ ] Support Claude 3.5 Sonnet as an alternative vision model via a `--model` flag
- [ ] Stream the GPT-4o reasoning JSON as it arrives rather than waiting for the full response
- [ ] Accept images larger than 4 MB by auto-downscaling before the DALL-E call
- [ ] Add a history panel that keeps the last N edits in the session

## License

MIT — see LICENSE.

---

Built autonomously by [autodev](https://github.com/RitikPatill/autodev),
a multi-agent orchestrator I designed. Each commit in this repo was
authored by me; the implementation work was performed by Sonnet under
the orchestrator's control. Read the orchestrator's README to see how.
