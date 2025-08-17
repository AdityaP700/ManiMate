# app/tasks.py
import subprocess
import tempfile
import os
import sys
import shutil
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs
from app.core.logging import logger
celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

MIKTEX_BIN_PATH = r"C:\Program Files\MiKTeX\miktex\bin\x64"

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    [FINAL CORRECTED VERSION] This version maps the descriptive quality names
    (e.g., '3b1b-style') to the correct single-letter flags required by ManimCE.
    """
    logger.info(f"Celery worker received render task for scene: {scene_name}")
    logger.debug(f"--- Code to be rendered for {scene_name} ---\n{manim_code}\n--------------------")
    try:
        latex_path = os.path.join(MIKTEX_BIN_PATH, "latex.exe")
        if not os.path.exists(latex_path):
            return {"status":"Failure", "message":"CRITICAL: latex.exe not found."}

        python_executable = sys.executable
        corrected_code = manim_code.replace("from manimlib import *", "from manim import *")

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            config_path = os.path.join(temp_dir, "manim.cfg")
            config_content = f"[CLI]\ntex_executable = {latex_path.replace('\\', '/')}\n"
            
            with open(config_path, "w") as f:
                f.write(config_content)
            with open(scene_file_path, "w", encoding="utf-8") as f:
                f.write(corrected_code)

            # --- THE FINAL, CRITICAL FIX ---
            # Map descriptive quality names to Manim's single-letter flags.
            QUALITY_MAP = {
                "minimal": "-ql",
                "draft": "-ql",
                "low": "-ql",
                "polished": "-qm",
                "medium": "-qm",
                "3b1b-style": "-qh", # 3b1b-style implies high quality
                "high": "-qh",
                "production": "-qk" # For 4k if needed
            }
            # Default to low quality if an unknown string is passed.
            quality_flag = QUALITY_MAP.get(quality, "-ql")

            # Also map to the correct output directory name
            QUALITY_DIR_MAP = {
                "-ql": "480p15",
                "-qm": "720p30",
                "-qh": "1080p60",
                "-qk": "2160p60"
            }
            quality_dir = QUALITY_DIR_MAP.get(quality_flag, "480p15")
            output_file_path = os.path.join(temp_dir, "media", "videos", "scene", quality_dir, f"{scene_name}.mp4")

            # The command is now correct and uses the mapped flag.
            command = [
                python_executable, "-m", "manim",
                scene_file_path, scene_name, quality_flag,
                "--renderer=cairo"
            ]

            process = subprocess.Popen(
                command, cwd=temp_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8'
            )
            stdout, stderr = process.communicate()
            
            if not os.path.exists(output_file_path):
                return { "status": "FAILURE", "message": "Render completed, but the output file path was incorrect or not found.", "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"}

            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)
            return { "status": "success", "url": public_url, "logs": stdout }

    except Exception as e:
        return { "status": "FAILURE", "message": f"An unexpected error occurred: {str(e)}", "logs": "" }