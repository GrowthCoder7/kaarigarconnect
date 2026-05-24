import asyncio
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.agents.formfill_agent import extract_form_data
from app.workers.playwright_worker import fill_udyam_form, replay_mock_events
from app.core.config import settings

from fastapi import UploadFile, File, Form
from app.workers.ocr_worker import extract_from_image, flatten_ocr_result
from app.agents.cataloguing_agent import catalogue_product

router = APIRouter(prefix="/automate", tags=["automation"])

# In-memory job store (Redis in production)
_jobs: dict = {}


# ── DTOs ──────────────────────────────────────────────────────────────

class FormFillRequest(BaseModel):
    artisan_id: str
    scheme_id: str
    profile: dict           # raw artisan profile from onboarding
    demo_mode: bool = True

class FormFillResponse(BaseModel):
    job_id: str
    ws_channel: str
    status: str = "queued"


# ── REST: Start a form-fill job ────────────────────────────────────────

@router.post("/start", response_model=FormFillResponse)
async def start_form_fill(req: FormFillRequest):
    """
    1. Extract structured form data from artisan profile via Gemini
    2. Create a job
    3. Return job_id + ws_channel for frontend to connect
    """
    job_id = str(uuid.uuid4())
    ws_channel = f"playwright_{job_id}"

    # Extract form data immediately (fast, ~1-2s)
    form_data = await extract_form_data(req.profile)

    _jobs[job_id] = {
        "status": "ready",
        "form_data": form_data,
        "scheme_id": req.scheme_id,
        "artisan_id": req.artisan_id,
        "demo_mode": req.demo_mode,
        "ws_channel": ws_channel,
        "events": []
    }

    return FormFillResponse(
        job_id=job_id,
        ws_channel=ws_channel
    )


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Poll job status — used as fallback if WebSocket disconnects."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "success": True,
        "data": {
            "job_id": job_id,
            "status": job["status"],
            "events": job["events"]
        }
    }


# ── WebSocket: Stream form-fill events ────────────────────────────────

@router.websocket("/ws/playwright/{job_id}")
async def playwright_stream(websocket: WebSocket, job_id: str):
    """
    Frontend connects here after calling /start.
    Triggers Playwright worker and streams events in real time.
    """
    await websocket.accept()

    job = _jobs.get(job_id)
    if not job:
        await websocket.send_json({"type": "FATAL_ERROR", "message": "Job not found"})
        await websocket.close()
        return

    _jobs[job_id]["status"] = "running"

    async def emit(event: dict):
        """Send event to WebSocket + store in job history."""
        _jobs[job_id]["events"].append(event)
        try:
            await websocket.send_json(event)
        except Exception:
            pass  # Client disconnected — keep running, events stored

    try:
        import platform
        use_mock = settings.demo_mode or job["demo_mode"] or platform.system() == "Windows"

        if use_mock:
            await replay_mock_events(emit)
        else:
            await fill_udyam_form(
                form_data=job["form_data"],
                emit=emit,
                demo_mode=False
            )
        _jobs[job_id]["status"] = "complete"

    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        await emit({"type": "FATAL_ERROR", "message": str(e), "timestamp": ""})

    finally:
        try:
            await websocket.close()
        except Exception:
            pass

# ── OCR endpoint ──────────────────────────────────────────────────────

@router.post("/ocr")
async def ocr_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="aadhaar")
):
    """Upload document image → get structured extracted data."""
    image_bytes = await file.read()
    result = await extract_from_image(image_bytes, doc_type)
    flat   = flatten_ocr_result(result)
    return {
        "success": True,
        "data": {
            "extracted": result,
            "flat":      flat       # ready for form injection
        }
    }


# ── Catalogue start endpoint ──────────────────────────────────────────

class CatalogueRequest(BaseModel):
    artisan_id: str
    artisan_profile: dict
    material_cost: float = 0
    hours_spent: float = 0

@router.post("/catalogue/start")
async def start_catalogue(
    file: UploadFile = File(...),
    artisan_id: str = Form(...),
    artisan_profile: str = Form(...),   # JSON string
    material_cost: float = Form(0),
    hours_spent: float = Form(0)
):
    """Upload product image → returns job_id + ws_channel."""
    job_id     = str(uuid.uuid4())
    ws_channel = f"catalogue_{job_id}"
    profile    = json.loads(artisan_profile)

    image_bytes = await file.read()

    _jobs[job_id] = {
        "type":          "catalogue",
        "status":        "ready",
        "image_bytes":   image_bytes,
        "artisan_id":    artisan_id,
        "profile":       profile,
        "material_cost": material_cost,
        "hours_spent":   hours_spent,
        "ws_channel":    ws_channel,
        "result":        None,
        "events":        []
    }

    return {"success": True, "data": {"job_id": job_id, "ws_channel": ws_channel}}


# ── Catalogue WebSocket stream ────────────────────────────────────────

@router.websocket("/ws/catalogue/{job_id}")
async def catalogue_stream(websocket: WebSocket, job_id: str):
    """Frontend connects → triggers Vision analysis → streams CatalogueEvents."""
    await websocket.accept()

    job = _jobs.get(job_id)
    if not job:
        await websocket.send_json({"type": "ERROR", "payload": {"message": "Job not found"}})
        await websocket.close()
        return

    _jobs[job_id]["status"] = "running"

    async def emit(event: dict):
        _jobs[job_id]["events"].append(event)
        try:
            await websocket.send_json(event)
        except Exception:
            pass

    try:
        result = await catalogue_product(
            image_bytes=job["image_bytes"],
            artisan_profile=job["profile"],
            emit=emit,
            material_cost=job["material_cost"],
            hours_spent=job["hours_spent"]
        )
        _jobs[job_id]["result"] = result
        _jobs[job_id]["status"] = "complete"

    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        await emit({"type": "ERROR", "payload": {"message": str(e)}})

    finally:
        try:
            await websocket.close()
        except Exception:
            pass