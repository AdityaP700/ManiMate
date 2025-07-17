# app/routes/render.py

from pydantic import BaseModel
from app.services.llm import generate_manim_code
from app.tasks import render_manim_scene
from app.services.validator import validate_manim_code
from app.utils.helpers import extract_scene_name
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from app.tasks import render_manim_scene
from app.tasks import celery 
router = APIRouter()

class RenderRequest(BaseModel):
    prompt: str
    quality: str = "low"  


@router.post("/render")
async def render(request: RenderRequest):
    manim_code = generate_manim_code(request.prompt)

    if not validate_manim_code(manim_code):
        raise HTTPException(status_code=400, detail="Code validation failed. The AI model may have returned invalid code.")

    scene_name = extract_scene_name(manim_code)

    task = render_manim_scene.delay(manim_code, scene_name, request.quality)
    
    return {"message": "Rendering started", "scene_name": scene_name, "task_id": task.id}

@router.get("/status/{task_id}")
async def check_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)

    status = task_result.status
    result = task_result.result

    if status == "PENDING":
        return {"status": "PENDING"}

    elif status == "STARTED":
        return {"status": "IN_PROGRESS"}

    elif status == "SUCCESS":
        return {
            "status": "SUCCESS",
            "url": result.get("url")  
        }

    elif status == "FAILURE":
        return {
            "status": "FAILURE",
            "error_log": result.get("message") if isinstance(result, dict) else str(result)
        }

    else:
        return {"status": status}

  