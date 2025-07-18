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

    if task_result.ready():
        # The task has finished. Now check the *result* of the task.
        result = task_result.result
        if result.get("status") == "success":
            return {"status": "SUCCESS", "url": result.get("url")}
        else:
            # The task finished, but with an internal failure.
            return {"status": "FAILURE", "error": result.get("message"), "logs": result.get("logs")}
    else:
        # The task is still running or pending.
        return {"status": "IN_PROGRESS"}

  