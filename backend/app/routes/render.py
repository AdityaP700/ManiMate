# app/routes/render.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm import generate_manim_code
from app.tasks import render_manim_scene

router = APIRouter()

class RenderRequest(BaseModel):
    prompt: str
    scene_name: str = "MyManimScene"

@router.post("/render")
async def render(request: RenderRequest):
    # 1. Generate Manim code from the prompt
    manim_code = generate_manim_code(request.prompt)
    
    # For now, let's assume a scene name. In the future, you could parse this from the code.
    
    # 2. Start the rendering task in the background
    task = render_manim_scene.delay(manim_code, request.scene_name)
    
    return {"message": "Rendering started", "task_id": task.id}