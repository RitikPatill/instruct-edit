# InstructEdit

A locally-runnable web app that edits images from free-form natural language instructions — no fine-tuning, no local GPU required.

The core idea is a **two-stage LLM chain** that turns a vague instruction like _"make it sunset"_ into a precise, region-aware inpainting prompt before touching the image.

---

## What works now (M1)

- Python package scaffold under `src/instruct_edit/` (`__version__ = "0.1.0"`)
- `requirements.txt` with pinned versions: FastAPI 0.115, Uvicorn 0.32, OpenAI SDK 1.54, Pillow 11, python-dotenv, Jinja2, python-multipart
- `.env.example` documenting required environment variables
- MIT license and `.gitignore`
- `demo/` directory placeholder for the M6 screen recording

Application code (routers, templates, pipeline logic) is added in M2–M5.

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
┌─────────────────┐
│  DALL-E 3 Edit  │  → edited image (base64)
└─────────────────┘
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
  "region":     "sky in the upper third of the image",
  "preserve":   "buildings, foreground, lighting on streets",
  "prompt":     "golden-hour sunset sky, warm orange and pink hues, photorealistic",
  "confidence": "high — sky is clearly separable from the subject"
}
```

This decomposition step is what makes the edits coherent. Rather than blindly passing the user's words to DALL-E, the reasoning layer ensures the model understands *what* to change and *what not* to touch.

### Stage 2 — Edit Execution (`POST /edit`)

The refined prompt from Stage 1 is sent to DALL-E 3's image-edit endpoint. The response (base64-encoded PNG) is returned alongside the original image so the user can compare them side-by-side in the browser.

---

## Project layout

```
instruct-edit/
├── src/
│   ├── __init__.py
│   └── instruct_edit/
│       └── __init__.py       # package version: 0.1.0
├── demo/                     # screen-recorded GIF added in M6
├── .env.example              # required environment variables
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

> Application code (`app.py`, routers, templates) is added in later milestones.

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

# 5. Run the development server  (available from M2 onwards)
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
- [ ] **M2** — FastAPI app skeleton, `/analyze` and `/edit` endpoints stubbed
- [ ] **M3** — GPT-4o vision call with structured output
- [ ] **M4** — DALL-E 3 edit call wired up end-to-end
- [ ] **M5** — Jinja2 + vanilla-JS frontend with drag-and-drop upload
- [ ] **M6** — Demo GIF, polished README, final cleanup

---

## License

MIT © 2026 Ritik
