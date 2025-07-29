# app/tasks.py
import subprocess
import tempfile
import os
import sys
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    [FINAL VERSION] Renders using Manim Community Edition with the
    reliable Cairo software renderer, which avoids all graphics driver issues.
    """
    try:
        python_executable = sys.executable
        # Ensure the AI-generated code uses the correct import for ManimCE
        corrected_code = manim_code.replace("from manimlib import *", "from manim import *")

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            output_file_name = f"{scene_name}.mp4"
            output_file_path = os.path.join(temp_dir, output_file_name)

            with open(scene_file_path, "w") as f:
                f.write(corrected_code)

            # ManimCE uses different quality flags
            QUALITY_MAP = {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qk"}
            quality_flag = QUALITY_MAP.get(quality, "-ql")

            # --- THE NEW, RELIABLE COMMAND ---
            command = [
                python_executable,
                "-m", "manim",
                scene_file_path,
                scene_name,
                quality_flag,
                "--renderer=cairo", # Use the software renderer
                "-o", output_file_name # Directly specify output file
            ]

            process = subprocess.Popen(
                command,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
            )
            
            stdout, stderr = process.communicate()
            
            if not os.path.exists(output_file_path):
                return { "status": "FAILURE", "message": "Render process finished but no output file was found.", "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"}

            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)
            return { "status": "success", "url": public_url, "logs": stdout }

    except Exception as e:
        return { "status": "FAILURE", "message": f"An unexpected error occurred: {str(e)}", "logs": "" }