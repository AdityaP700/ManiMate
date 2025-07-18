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

# app/tasks.py
# ... (all your imports) ...

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    [FINAL VERSION] This version corrects the AI's import statement from
    'from manim import *' to 'from manimlib import *' before rendering.
    """
    try:
        python_executable = sys.executable

        # --- THE FINAL, CRITICAL FIX ---
        # Automatically replace the wrong import with the correct one for manimgl.
        corrected_code = manim_code.replace("from manim import *", "from manimlib import *")

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(corrected_code) # <-- Use the corrected code

            QUALITY_FLAGS = {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qk"}
            quality_flag = QUALITY_FLAGS.get(quality, "-ql")

            command = [
                python_executable,
                "-m", "manimlib",
                scene_file_path,
                scene_name,
                "-w",
                "-p",
                quality_flag,
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
            
            output_file_path = os.path.join(temp_dir, "media", "videos", "scene", quality_flag.replace('-', ''), f"{scene_name}.mp4")

            if not os.path.exists(output_file_path):
                alt_path = os.path.join(temp_dir, "media", "videos", "scene", "1080p60", f"{scene_name}.mp4")
                if not os.path.exists(alt_path):
                    return { "status": "FAILURE", "message": "Render process finished but no output file was found.", "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"}
                output_file_path = alt_path

            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)
            return { "status": "success", "url": public_url, "logs": stdout }

    except Exception as e:
        return { "status": "FAILURE", "message": f"An unexpected error occurred: {str(e)}", "logs": "" }
    try:
        python_executable = sys.executable
        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(manim_code)

            QUALITY_FLAGS = {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qk"}
            quality_flag = QUALITY_FLAGS.get(quality, "-ql")

            command = [
                python_executable,
                "-m", "manimlib",
                scene_file_path,
                scene_name,
                "-w",
                "-p",
                quality_flag,
            ]

            process = subprocess.Popen(
                command,
                cwd=temp_dir, # Run from the temp directory to keep media files contained
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )

            stdout, stderr = process.communicate()
            
            # Reverting to the output path for the -w flag
            output_file_path = os.path.join(temp_dir, "media", "videos", "scene", quality_flag.replace('-', ''), f"{scene_name}.mp4")

            if not os.path.exists(output_file_path):
                alt_path = os.path.join(temp_dir, "media", "videos", "scene", "1080p60", f"{scene_name}.mp4")
                if not os.path.exists(alt_path):
                    return { "status": "FAILURE", "message": "Render process finished but no output file was found.", "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"}
                output_file_path = alt_path

            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)
            return { "status": "success", "url": public_url, "logs": stdout }

    except Exception as e:
        return { "status": "FAILURE", "message": f"An unexpected error occurred: {str(e)}", "logs": "" }