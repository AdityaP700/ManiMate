# app/tasks.py
import subprocess
import tempfile
import os
import sys
import shutil
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    [FINAL HEADLESS FIX] This version sets an environment variable to force a
    headless graphics backend, preventing the low-level crash.
    """
    try:
        python_executable = sys.executable
        # Gemini is now generating the correct code, so the replace() is just a safeguard.
        corrected_code = manim_code.replace("from manim import *", "from manimlib import *")

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(corrected_code)

            # --- THE FINAL, DEFINITIVE FIX ---
            # Create a clean environment and set the PYGLET_HEADLESS variable.
            # This tells the graphics library not to look for a real screen.
            process_env = os.environ.copy()
            process_env['PYGLET_HEADLESS'] = 'true'

            # The command itself is correct.
            command = [python_executable, "-m", "manimlib", scene_file_path, scene_name, "-w", "-p", "-ql"]

            # We can go back to simpler piping now that we know the issue isn't lost logs.
            process = subprocess.Popen(
                command,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                env=process_env # <--- Pass the special headless environment
            )
            
            stdout, stderr = process.communicate()
            
            output_file_path = os.path.join(temp_dir, "media", "videos", "scene", "l", f"{scene_name}.mp4")

            if not os.path.exists(output_file_path):
                # Fallback check for different quality path just in case
                alt_path = os.path.join(temp_dir, "media", "videos", "scene", "1080p60", f"{scene_name}.mp4")
                if not os.path.exists(alt_path):
                    return { "status": "FAILURE", "message": "Render process finished but no output file was found.", "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"}
                output_file_path = alt_path

            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)
            return { "status": "success", "url": public_url, "logs": stdout }

    except Exception as e:
        return { "status": "FAILURE", "message": f"An unexpected error occurred: {str(e)}", "logs": "" }