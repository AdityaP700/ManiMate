# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import render

app = FastAPI(
    title="ManiMate API",
    description="AI-Powered Manim Animation Generator",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(render.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the ManiMate API"}

# You can add more routes here, for example, to check the status of a rendering task
# @app.get("/status/{task_id}")
# def get_status(task_id: str):
#     task = render_manim_scene.AsyncResult(task_id)
#     return {"status": task.status, "result": task.result}