import asyncio
import json
import uuid
import platform
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.agents.formfill_agent import extract_form_data
from app.workers.playwright_worker import fill_udyam_form, replay_mock_events
from app.workers.ocr_worker import extract_from_image, categorize_ocr_result
from app.agents.cataloguing_agent import catalogue_product
from app.core.config import settings
from app.core.redis_client import (
    set_job, get_job, update_job,
    append_event, get_events,
    set_image_bytes, get_image_bytes
)

router = APIRouter(prefix="/automate", tags=["automation"])


# ── DTOs ──────────────────────────────────────────────────────────────

class FormFillRequest(BaseModel):
    artisan_id: str
    scheme_id: str
    profile: dict
    demo_mode: bool = True

class FormFillResponse(BaseModel):
    job_id: str
    ws_channel: str
    status: str = "queued"


# ── Form fill: start ──────────────────────────────────────────────────

@router.post("/start", response_model=FormFillResponse)
async def start_form_fill(req: FormFillRequest):
    job_id     = str(uuid.uuid4())
    ws_channel = f"playwright_{job_id}"
    form_data  = await extract_form_data(req.profile)

    set_job(job_id, {
        "status":     "ready",
        "form_data":  form_data,
        "scheme_id":  req.scheme_id,
        "artisan_id": req.artisan_id,
        "demo_mode":  req.demo_mode,
        "ws_channel": ws_channel,
    })

    return FormFillResponse(job_id=job_id, ws_channel=ws_channel)


# ── Form fill: status poll ────────────────────────────────────────────

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "status": job.get("status"),
            "events": get_events(job_id)
        }
    }


# ── Form fill: WebSocket stream ───────────────────────────────────────

@router.websocket("/ws/playwright/{job_id}")
async def playwright_stream(websocket: WebSocket, job_id: str):
    await websocket.accept()

    job = get_job(job_id)
    if not job:
        await websocket.send_json({"type": "FATAL_ERROR", "message": "Job not found"})
        await websocket.close()
        return

    update_job(job_id, {"status": "running"})

    async def emit(event: dict):
        append_event(job_id, event)
        try:
            await websocket.send_json(event)
        except Exception:
            pass

    try:
        use_mock = job["demo_mode"]
        if use_mock:
            await replay_mock_events(emit)
        else:
            await fill_udyam_form(
                form_data=job["form_data"],
                emit=emit,
                demo_mode=False
            )
        update_job(job_id, {"status": "complete"})

    except Exception as e:
        update_job(job_id, {"status": "failed"})
        await emit({"type": "FATAL_ERROR", "message": str(e)})

    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# ── OCR ───────────────────────────────────────────────────────────────

@router.post("/ocr")
async def ocr_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="aadhaar")
):
    image_bytes = await file.read()
    result = await extract_from_image(image_bytes, doc_type)
    
    # Tri-state categorization for the frontend
    categorized = categorize_ocr_result(result)
    
    return {
        "success": True, 
        "data": {
            "raw_extracted": result, 
            "categorized": categorized
        }
    }


# ── Catalogue: start ──────────────────────────────────────────────────

@router.post("/catalogue/start")
async def start_catalogue(
    file: UploadFile        = File(...),
    artisan_id: str         = Form(...),
    artisan_profile: str    = Form(...),
    material_cost: float    = Form(0),
    hours_spent: float      = Form(0)
):
    job_id      = str(uuid.uuid4())
    ws_channel  = f"catalogue_{job_id}"
    profile     = json.loads(artisan_profile)
    image_bytes = await file.read()

    # Store image bytes separately (not JSON serializable)
    set_image_bytes(job_id, image_bytes)

    set_job(job_id, {
        "type":          "catalogue",
        "status":        "ready",
        "artisan_id":    artisan_id,
        "profile":       profile,
        "material_cost": material_cost,
        "hours_spent":   hours_spent,
        "ws_channel":    ws_channel,
        "result":        None,
    })

    return {"success": True, "data": {"job_id": job_id, "ws_channel": ws_channel}}


# ── Catalogue: WebSocket stream ───────────────────────────────────────

@router.websocket("/ws/catalogue/{job_id}")
async def catalogue_stream(websocket: WebSocket, job_id: str):
    await websocket.accept()

    job = get_job(job_id)
    if not job:
        await websocket.send_json({"type": "ERROR", "payload": {"message": "Job not found"}})
        await websocket.close()
        return

    image_bytes = get_image_bytes(job_id)
    if not image_bytes:
        await websocket.send_json({"type": "ERROR", "payload": {"message": "Image not found"}})
        await websocket.close()
        return

    update_job(job_id, {"status": "running"})

    async def emit(event: dict):
        append_event(job_id, event)
        try:
            await websocket.send_json(event)
        except Exception:
            pass

    try:
        result = await catalogue_product(
            image_bytes=image_bytes,
            artisan_profile=job["profile"],
            emit=emit,
            material_cost=job["material_cost"],
            hours_spent=job["hours_spent"]
        )
        update_job(job_id, {"status": "complete", "result": result})

    except Exception as e:
        update_job(job_id, {"status": "failed"})
        await emit({"type": "FATAL_ERROR", "message": str(e)})

    finally:
        try:
            await websocket.close()
        except Exception:
            pass