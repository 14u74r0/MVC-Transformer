import io
import time

import torch
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError

from app import config

router = APIRouter()


@router.get("/")
def index():
    return FileResponse(config.VIEWS_DIR / "index.html")


@router.get("/api/health")
def health(request: Request):
    return request.app.state.model.info()


@router.post("/api/analyze")
def analyze(request: Request, image: UploadFile = File(...), question: str = Form("")):
    limit = config.MAX_UPLOAD_MB * 1024 * 1024
    data = image.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"La imagen supera los {config.MAX_UPLOAD_MB} MB.")

    try:
        pil_image = Image.open(io.BytesIO(data))
        pil_image.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "El archivo no es una imagen válida.")

    question = question.strip()
    if len(question) > config.MAX_QUESTION_CHARS:
        raise HTTPException(400, f"La pregunta supera los {config.MAX_QUESTION_CHARS} caracteres.")

    model = request.app.state.model
    start = time.perf_counter()
    try:
        text = model.ask(pil_image, question) if question else model.describe(pil_image)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise HTTPException(503, "Se quedó sin memoria de GPU. Probá con una imagen más chica o un modelo más liviano.")

    return {
        "text": text,
        "mode": "ask" if question else "describe",
        "seconds": round(time.perf_counter() - start, 1),
        "device": model.info()["device"],
    }
