# app/tasks.py

import subprocess
import tempfile
import os
import sys
import shutil
import re
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

MIKTEX_BIN_PATH = r"C:\Program Files\MiKTeX\miktex\bin\x64"

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    Renders a Manim scene using the Community Edition with the Cairo software renderer.
    Supports MiKTeX LaTeX integration and uploads output to GCS.
    """
    try:
        # Check for LaTeX executable
        latex_path = os.path.join(MIKTEX_BIN_PATH, "latex.exe")
        if not os.path.exists(latex_path):
            return {
                "status": "FAILURE",
                "message": "CRITICAL: latex.exe not found.",
                "logs": "MiKTeX LaTeX not available. Cannot render math text."
            }

        python_executable = sys.executable
        corrected_code = manim_code.replace("from manimlib import *", "from manim import *")
        
        # Sanitize scene name
        scene_name = re.sub(r"[^\w\-]", "_", scene_name)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Write user code to temp scene file
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w", encoding="utf-8") as f:
                f.write(corrected_code)

            # Write manim.cfg with LaTeX path
            config_path = os.path.join(temp_dir, "manim.cfg")
            config_content = f"[CLI]\ntex_executable = {latex_path.replace('\\', '/')}\n"
            with open(config_path, "w") as f:
                f.write(config_content)

            # Determine output directory
            QUALITY_DIRS = {
                "low": "480p15",
                "medium": "720p30",
                "high": "1080p60",
                "production": "4k60"
            }
            quality_dir = QUALITY_DIRS.get(quality, "480p15")
            output_file_path = os.path.join(
                temp_dir, "media", "videos", "scene", quality_dir, f"{scene_name}.mp4"
            )

            # Build Manim render command
            command = [
                python_executable, "-m", "manim",
                scene_file_path, scene_name,
                f"-q{quality[0]}",  # -ql, -qm, -qh, etc.
                "--renderer=cairo"
            ]

            process = subprocess.Popen(
                command,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout, stderr = process.communicate()

            # Check if output file was generated
            if not os.path.exists(output_file_path):
                return {
                    "status": "FAILURE",
                    "message": "Render completed, but the output file path was incorrect or not found.",
                    "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                }

            # Upload to GCS
            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)

            return {
                "status": "success",
                "url": public_url,
                "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            }

    except Exception as e:
        return {
            "status": "FAILURE",
            "message": f"An unexpected error occurred: {str(e)}",
            "logs": ""
        }
