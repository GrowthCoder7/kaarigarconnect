import asyncio
import json
import uuid
import platform
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import base64

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
from app.workers.voice_worker import process_audio_chunk, get_initial_greeting

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
    files: List[UploadFile] = File(...),  # Notice it is now 'files' and 'List'
    doc_type: str = Form(default="aadhaar")
):
    # Read all uploaded files into a list of bytes
    image_bytes_list = [await f.read() for f in files]
    
    # Pass the entire list to the worker
    result = await extract_from_image(image_bytes_list, doc_type)
    
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

# ── Voice Onboarding: Live Audio Stream ────────────────────────────────

@router.websocket("/ws/onboard/voice/{artisan_id}")
async def voice_onboarding_stream(websocket: WebSocket, artisan_id: str):
    await websocket.accept()
    
    # Track the conversational memory thread just for this active websocket session
    chat_history = []
    current_language = "auto"
    
    # Send an initial welcome state so the frontend knows the channel is awake
    await websocket.send_json({
        "type": "STATUS_UPDATE",
        "payload": {"message": "Voice channel ready. Listening..."}
    })

    try:
        greeting = await get_initial_greeting()
        if greeting:
            # Save the AI's first question into the LLM's brain so it knows what it asked
            chat_history.append({"ai": greeting["ai_text"]})
            
            audio_base64 = base64.b64encode(greeting["ai_audio_bytes"]).decode("utf-8")
            
            # Fire the payload to Person A's UI instantly
            await websocket.send_json({
                "type": "SPEAKING",
                "payload": {
                    "user_transcription": "", # No user text yet
                    "ai_response_text": greeting["ai_text"], 
                    "audio_data": f"data:audio/mp3;base64,{audio_base64}",
                    "extracted_form_data": {} 
                }
            })
    except Exception as e:
        print(f"[Voice Stream] Greeting error: {e}")

    try:
        while True:
            # Expecting binary audio frames (WebM/Opus) coming straight from the client's microphone chunking buffer
            data = await websocket.receive_bytes()
            
            if not data or len(data) < 100:
                continue

            # Notify the client that the worker has stopped listening and started crunching numbers
            await websocket.send_json({"type": "PROCESSING", "payload": {}})

            # Run through the STT -> LLM -> TTS pipeline
            pipeline_result = await process_audio_chunk(data, chat_history,current_language)
            
            if pipeline_result:
                # Append to our local in-memory thread history
                chat_history.append({"user": pipeline_result["user_text"]})
                chat_history.append({"ai": pipeline_result["ai_text"]})

                current_language = pipeline_result.get("language_code", current_language)
                # Encode the raw MP3 audio bytes to a browser-ready Base64 string
                audio_base64 = base64.b64encode(pipeline_result["ai_audio_bytes"]).decode("utf-8")

                # Emit the synchronized result back to Person A's UI engine
                await websocket.send_json({
                    "type": "SPEAKING",
                    "payload": {
                        "user_transcription": pipeline_result["user_text"],
                        "ai_response_text": pipeline_result["ai_text"],
                        "audio_data": f"data:audio/mp3;base64,{audio_base64}",
                        "extracted_form_data": pipeline_result["extracted_data"]
                    }
                })
            else:
                await websocket.send_json({
                    "type": "STATUS_UPDATE",
                    "payload": {"message": "Could not clear audio layer clearly. Try again."}
                })

    except WebSocketDisconnect:
        print(f"[Voice Stream] Artisan disconnected: {artisan_id}")
    except Exception as e:
        print(f"[Voice Stream] Fatal session exception: {e}")
        try:
            await websocket.send_json({"type": "ERROR", "payload": {"message": str(e)}})
        except Exception:
            pass

from fastapi.responses import StreamingResponse
import io

class TTSRequest(BaseModel):
    text: str
    lang_code: str = "en"

@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    import edge_tts
    
    VOICE_MAP = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "ta": "ta-IN-PallaviNeural",
        "te": "te-IN-ShrutiNeural",
        "bn": "bn-IN-TanishaaNeural",
        "kan": "kn-IN-SapnaNeural",  # note: guide uses 'kan', TTS uses 'kn'
        "mr": "mr-IN-AarohiNeural",
        "gu": "gu-IN-DhwaniNeural",
    }
    
    voice = VOICE_MAP.get(req.lang_code, "en-IN-NeerjaNeural")
    
    # Truncate to avoid edge-tts limits
    text = req.text[:3000]
    
    output_path = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        with open(output_path, "rb") as f:
            audio_bytes = f.read()
            
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
    finally:
        import os
        if os.path.exists(output_path):
            os.remove(output_path)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response

@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    # ... your existing code ...
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3",
            "Access-Control-Allow-Origin": "*",   # ADD this
        }
    )