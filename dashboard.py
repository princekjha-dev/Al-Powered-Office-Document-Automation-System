#!/usr/bin/env python3
"""
FastAPI dashboard and REST API aligned with README endpoints.
"""

import os
import sys
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import Config
from src.models.storage import UserGalleryStorage
from src.models.user import UserManager
from src.services.ai_generation import AIGenerationService
from src.services.document_categorization import DocumentCategorization
from src.services.document_comparison import DocumentComparison
from src.services.document_generator import DocumentGenerator
from src.services.document_quality import DocumentQuality
from src.services.document_reader import DocumentReader
from src.services.image_gallery import ImageGalleryService
from src.services.image_generator import ImageGenerator
from src.services.language_detection import LanguageDetection
from src.utils.helpers import format_file_size, get_logger

Config.create_directories()
logger = get_logger(__name__)

app = FastAPI(title="Intellidoc API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_manager = UserManager(data_dir=Config.USERS_DIR)
storage = UserGalleryStorage(base_dir=Config.GALLERIES_DIR)
gallery_service = ImageGalleryService(storage)
ai_service = AIGenerationService()
image_service = ImageGenerator()
category_service = DocumentCategorization()
quality_service = DocumentQuality()
language_service = LanguageDetection()
compare_service = DocumentComparison()

# Simple in-memory session state for dashboard usage
SESSION_STATE: Dict[str, Any] = {
    "active_document_text": "",
    "active_document_name": "",
    "history": [],
    "stats": {"documents": 0, "questions": 0, "images": 0},
}


def _response(data: Dict[str, Any], confidence: float = 1.0, warnings: Optional[list] = None) -> Dict[str, Any]:
    return {"confidence": confidence, "warnings": warnings or [], **data}


async def _read_upload(file: UploadFile) -> str:
    if not file.filename or not DocumentReader.is_supported_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    temp_path = os.path.join(Config.TEMP_DIR, file.filename)
    try:
        with open(temp_path, "wb") as out:
            out.write(await file.read())
        text = DocumentReader.extract_text(temp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted from document")
        return text
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    text = await _read_upload(file)
    lang = language_service.detect_language(text)
    category, category_conf = category_service.categorize_document(text)
    quality = quality_service.score_document(text)
    analysis = ai_service.analyze_document(text)

    SESSION_STATE["active_document_text"] = text
    SESSION_STATE["active_document_name"] = file.filename or ""
    SESSION_STATE["stats"]["documents"] += 1

    return _response(
        {
            "success": True,
            "file_name": file.filename,
            "language": lang,
            "category": {"name": category, "confidence": category_conf},
            "quality": quality,
            "analysis": analysis,
        },
        confidence=0.9,
    )


@app.post("/api/chat")
async def chat(message: str = Form(...)):
    text = SESSION_STATE.get("active_document_text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No active document in session")
    prompt = (
        "Answer the user's question using only this document.\n\n"
        f"Document:\n{text[:12000]}\n\nQuestion:\n{message}"
    )
    answer = ai_service.call_ai(prompt)
    verified = ai_service.verify_response(answer, text)
    SESSION_STATE["history"].append({"role": "user", "content": message})
    SESSION_STATE["history"].append({"role": "assistant", "content": verified})
    SESSION_STATE["stats"]["questions"] += 1
    return _response({"answer": verified}, confidence=0.85)


@app.post("/api/compare")
async def compare(file_a: UploadFile = File(...), file_b: UploadFile = File(...)):
    text_a = await _read_upload(file_a)
    text_b = await _read_upload(file_b)
    report = compare_service.generate_comparison_report(text_a, text_b, ai_service=ai_service)
    return _response({"comparison": report}, confidence=0.88)


@app.post("/api/generate/doc")
async def generate_doc(topic: str = Form(...), format: str = Form("docx")):
    content = ai_service.generate_document(topic)
    if format.lower() == "pdf":
        filepath = DocumentGenerator.generate_pdf(topic, content, output_dir=Config.TEMP_DIR)
    else:
        filepath = DocumentGenerator.generate_docx(topic, content, output_dir=Config.TEMP_DIR)
    return _response({"success": True, "file": filepath, "format": format.lower()}, confidence=0.9)


@app.post("/api/generate/image")
async def generate_image(prompt: str = Form(...), style: str = Form("realistic"), user_id: int = Form(0)):
    image_path = image_service.generate_from_prompt(prompt, style)
    if user_id:
        gallery_service.add_image(user_id, image_path, prompt, tags=["generated", style], style=style)
    SESSION_STATE["stats"]["images"] += 1
    return _response({"success": True, "image": image_path, "style": style}, confidence=0.8)


@app.post("/api/translate")
async def translate(target_language: str = Form(...)):
    text = SESSION_STATE.get("active_document_text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No active document in session")
    translated = language_service.translate(text, target_language, ai_service)
    return _response({"translated_text": translated, "target_language": target_language}, confidence=0.82)


@app.post("/api/errors")
async def errors():
    text = SESSION_STATE.get("active_document_text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No active document in session")
    issues = []
    if len(text.split()) < 100:
        issues.append({"severity": "warning", "message": "Document appears very short"})
    if "???" in text:
        issues.append({"severity": "warning", "message": "Suspicious placeholder markers found"})
    return _response({"issues": issues, "count": len(issues)}, confidence=0.75)


@app.post("/api/quality")
async def quality():
    text = SESSION_STATE.get("active_document_text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No active document in session")
    return _response({"quality": quality_service.score_document(text)}, confidence=0.86)


@app.post("/api/export")
async def export(format: str = Form("json"), user_id: int = Form(0)):
    payload = {
        "session": SESSION_STATE,
        "gallery": storage.export_user_gallery(user_id, export_format="json") if user_id else [],
    }
    return _response({"format": format, "data": payload}, confidence=0.9)


@app.get("/api/gallery")
async def gallery(user_id: int = 0, limit: int = 10):
    if not user_id:
        return _response({"images": [], "count": 0, "storage": "0 B"})
    images = gallery_service.get_gallery_summary(user_id, limit=limit)
    return _response(
        {
            "images": images,
            "count": len(images),
            "total": storage.get_user_images_count(user_id),
            "storage": format_file_size(storage.get_user_gallery_size(user_id)),
        }
    )


@app.get("/api/session")
async def session():
    return _response({"session": SESSION_STATE})


@app.get("/api/stats")
async def stats():
    return _response({"stats": SESSION_STATE["stats"]})


@app.delete("/api/session")
async def clear_session():
    SESSION_STATE["active_document_text"] = ""
    SESSION_STATE["active_document_name"] = ""
    SESSION_STATE["history"] = []
    return _response({"success": True})


@app.get("/api/health")
async def health():
    return _response({"status": "healthy", "provider": Config.AI_PROVIDER})


def run_dashboard(host: str = "0.0.0.0", port: int = 5000) -> None:
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_dashboard()
