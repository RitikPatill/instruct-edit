# InstructEdit

A locally-runnable web app that edits images from free-form natural language instructions — no fine-tuning, no local GPU required.

The core idea is a **two-stage LLM chain** that turns a vague instruction like _"make it sunset"_ into a precise, region-aware inpainting prompt before touching the image.

---

## What works now (M5)

- Python package scaffold under `src/instruct_edit/` (`__version__ = "0.1.0"`)
- `requirements.txt` with pinned versions: FastAPI 0.115, Uvicorn 0.32, OpenAI SDK 1.54, Pillow 11, python-dotenv, Jinja2, python-multipart, httpx 0.27
- `.env.example` documenting required environment variables
- MIT license and `.gitignore`
- `demo/` directory placeholder for the M6 screen recording
- `src/instruct_edit/analyzer.py` — vision analysis module: accepts a PIL `Image` and a plain-English instruction, base64-encodes the image, calls GPT-4o with a structured-output system prompt, validates the response against four required keys, and returns a `dict` ready for the edit stage
- `src/instruct_edit/editor.py` — edit execution module: takes the structured JSON from the analyzer and the original PIL Image, calls **DALL-E 2's edit endpoint** with a blank (edit-everywhere) mask, falls back to **DALL-E 3 generation** on `BadRequestError` (content policy / size), resizes the result back to original dimensions, and raises descriptive `RuntimeError`s for other API failures
- `src/instruct_edit/app.py` — FastAPI application with:
  - `GET /` — renders `templates/index.html` via Jinja2
  - `POST /analyze` — accepts multipart `image` + `instruction`, returns reasoning JSON (422 on empty instruction or malformed response)
  - `POST /edit` — runs the full two-stage pipeline, returns `{"analysis": {...}, "edited_image": "data:image/png;base64,…"}` (422 on ValueError, 502 on RuntimeError)
  - `/static` mounted for CSS/JS assets
- `templates/index.html` — full single-page UI (drag-and-drop upload, instruction input, before/after comparison, collapsible LLM reasoning)
- `static/style.css` — dark-themed stylesheet with CSS custom properties and responsive grid layout
- `static/app.js` — vanilla JS IIFE handling file selection, drag-and-drop preview, `POST /edit` fetch, and result rendering
- `tests/test_analyzer.py`, `tests/test_editor.py`, and `tests/test_app.py` — unit test suites (all mocked, no real API calls)

> **Note:** DALL-E 3 does not expose an edit/inpainting endpoint. When the DALL-E 2 edit call fails (e.g. content policy), the fallback uses DALL-E 3 `generate` — the original image pixels are discarded and the edit is prompt-only.

---

## Architecture

```
User image + instruction
       │
       ▼
┌─────────────────┐
│  GPT-4o Vision  │  → structured JSON (region, preserve, prompt, confidence)
└─────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  DALL-E 2 Edit (+ DALL-E 3 fallback) │  → edited image (PIL)
└──────────────────────────────────────┘
       │
       ▼
  Before / After comparison (browser)
```

---

## Two-stage pipeline

### Stage 1 — Vision Analysis (`POST /analyze`)

GPT-4o receives the original image and the raw user instruction. It returns a structured JSON object via function-calling:

```json
{
  "region_description": "sky in the upper third of the image",
  "preserve_elements":  "buildings, foreground, lighting on streets",
  "dalle_prompt":       "golden-hour sunset sky, warm orange and pink hues, photorealistic",
  "confidence":         "high — sky is clearly separable from the subject"
}
```

This decomposition step is what makes the edits coherent. Rather than blindly passing the user's words to DALL-E, the reasoning layer ensures the model understands *what* to change and *what not* to touch.

### Stage 2 — Edit Execution (`POST /edit`)

The refined prompt from Stage 1 is passed to `editor.py`. It calls the **DALL-E 2 edit endpoint** with a blank mask (edit everywhere), then resizes the result back to the original dimensions. If that call fails (content policy, unsupported size), it falls back to **DALL-E 3 generation** — in that case the original pixels are discarded and the edit is prompt-only. The returned PIL `Image` is what the web layer will serve for the before/after comparison.

> DALL-E 3 does not expose an inpainting/edit endpoint; the fallback is generation-only.

---

## Project layout

```
instruct-edit/
├── src/
│   ├── __init__.py
│   └── instruct_edit/
│       ├── __init__.py       # package version: 0.1.0
│       ├── analyzer.py       # Stage 1: GPT-4o vision → structured JSON
│       ├── editor.py         # Stage 2: DALL-E 2 edit (+ DALL-E 3 fallback)
│       └── app.py            # FastAPI application (GET /, POST /analyze, POST /edit)
├── templates/
│   └── index.html            # Jinja2 template (full UI added in M5)
├── static/
│   ├── style.css             # dark-themed CSS with responsive image-pair grid
│   └── app.js                # vanilla JS: drag-and-drop, fetch /edit, render results
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_editor.py
│   ├── test_app.py
│   └── fixtures/
│       └── sample.jpg
├── demo/                     # screen-recorded GIF added in M6
├── .env.example              # required environment variables
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/you/instruct-edit.git
cd instruct-edit

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and paste your OpenAI API key

# 5. Run the development server  (available from M4 onwards)
PYTHONPATH=src uvicorn instruct_edit.app:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Key from [platform.openai.com](https://platform.openai.com) |
| `LOG_LEVEL` | No | Python log level, default `INFO` |

---

## Roadmap

- [x] **M1** — Repo scaffold, package layout, pinned dependencies, license
- [x] **M2** — Vision analysis module (`analyzer.py`): GPT-4o vision call with structured JSON output, unit tests
- [x] **M3** — Edit execution module (`editor.py`): DALL-E 2 edit endpoint with blank mask, DALL-E 3 generation fallback, unit tests
- [x] **M4** — FastAPI app (`app.py`), `GET /`, `POST /analyze`, `POST /edit` endpoints, Jinja2 template placeholder, static dir, full test suite
- [x] **M5** — Jinja2 + vanilla-JS frontend: drag-and-drop upload, instruction input, collapsible LLM reasoning, before/after image comparison
- [ ] **M6** — Demo GIF, polished README, final cleanup

---

## License

MIT © 2026 Ritik
