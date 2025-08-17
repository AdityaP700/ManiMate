# app/routes/render.py

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict
from celery.result import AsyncResult

from app.core.logging import logger
from app.services.llm import generate_manim_code, ProviderType
from app.services.validator import validate_prompt, validate_manim_code
from app.utils.helpers import extract_scene_name
from app.tasks import render_manim_scene, celery

router = APIRouter()

# -------------------------------
# Request Schema
# -------------------------------
class RenderRequest(BaseModel):
    prompt: str
    quality: str = "polished"
    style: str = "educational"
    preferred_provider: ProviderType = "auto"
    # Note: API keys are now passed in headers, not the body.


# -------------------------------
# Render Endpoint
# -------------------------------
@router.post("/render")
async def render(
    request: RenderRequest,
    # --- BYOK: Accept keys securely via headers ---
    openai_api_key: Optional[str] = Header(None),
    gemini_api_key: Optional[str] = Header(None),
    deepseek_api_key: Optional[str] = Header(None)
):
    # --- Step 1: Validate the prompt ---
    is_valid, message = validate_prompt(request.prompt)
    if not is_valid:
        logger.warning("Rejected render request: %s", message)
        raise HTTPException(status_code=400, detail=message)
    logger.info("Prompt validated successfully for: %s", request.prompt)

    # --- Step 2: Collect user-supplied API keys ---
    user_api_keys: Dict[str, Optional[str]] = {
        "openai": openai_api_key,
        "gemini": gemini_api_key,
        "deepseek": deepseek_api_key,
    }

    # --- Step 3: Generate Manim code using the Intelligent Engine ---
    result = generate_manim_code(
        prompt=request.prompt,
        quality=request.quality,
        style=request.style,
        preferred_provider=request.preferred_provider,
        api_keys=user_api_keys,
    )

    if not result["success"]:
        logger.error("Code generation failed: %s", result["validation_result"])
        raise HTTPException(status_code=500, detail=result["validation_result"])

    manim_code = result["code"]
    scene_name = extract_scene_name(manim_code)
    logger.info("Code generated successfully using provider: %s (scene=%s)", result["provider_used"], scene_name)

    # --- Step 4: Validate generated code before queuing ---
    if not validate_manim_code(manim_code):
        logger.error("Invalid Manim code generated for prompt: %s", request.prompt)
        raise HTTPException(status_code=400, detail="Code validation failed. The AI model may have returned invalid code.")
    logger.info("Generated Manim code validated successfully")

    # --- Step 5: Queue the render task (non-blocking) ---
    task = render_manim_scene.delay(manim_code, scene_name, request.quality)
    logger.info("Queued render task for scene: %s (task_id=%s)", scene_name, task.id)

    return {
        "message": "Rendering started",
        "scene_name": scene_name,
        "task_id": task.id,
        "provider_used": result["provider_used"],
    }


# -------------------------------
# Status Endpoint
# -------------------------------
@router.get("/status/{task_id}")
async def check_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)

    if task_result.ready():
        result = task_result.result
        if result.get("status") == "success":
            logger.info("Task %s finished successfully (url=%s)", task_id, result.get("url"))
            return {"status": "SUCCESS", "url": result.get("url")}
        else:
            logger.error("Task %s failed: %s", task_id, result.get("message"))
            return {
                "status": "FAILURE",
                "error": result.get("message"),
                "logs": result.get("logs"),
            }
    else:
        logger.info("Task %s still in progress", task_id)
        return {"status": "IN_PROGRESS"}
