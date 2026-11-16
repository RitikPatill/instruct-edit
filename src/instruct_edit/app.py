import base64
import io
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from instruct_edit.analyzer import analyze
from instruct_edit.editor import edit

BASE_DIR = Path(__file__).resolve().parent.parent.parent

app = FastAPI(title="InstructEdit")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


async def analyze_endpoint(image: UploadFile, instruction: str = Form(...)):
    data = await image.read()
    img = Image.open(io.BytesIO(data)).copy()
    try:
        result = analyze(img, instruction)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return JSONResponse(result)


async def edit_endpoint(image: UploadFile, instruction: str = Form(...)):
    data = await image.read()
    img = Image.open(io.BytesIO(data)).copy()
    try:
        analysis = analyze(img, instruction)
        edited = edit(analysis, img)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    buf = io.BytesIO()
    edited.save(buf, format="PNG")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()
    data_url = f"data:image/png;base64,{encoded}"
    return JSONResponse({"analysis": analysis, "edited_image": data_url})


app.add_api_route("/", index, methods=["GET"])
app.add_api_route("/analyze", analyze_endpoint, methods=["POST"])
app.add_api_route("/edit", edit_endpoint, methods=["POST"])
