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
    Celery task that invokes the python interpreter with the 'manimlib' module,
    which is correct for the 'manimgl' package.
    """
    try:
        python_executable = sys.executable

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(manim_code)

            QUALITY_FLAGS = {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qk"}
            quality_flag = QUALITY_FLAGS.get(quality, "-ql")

            # --- THE CORRECT COMMAND FOR A CLEAN MANIMGL INSTALLATION ---
            command = [
                python_executable,
                "-m", "manimlib",  # This is the correct module for manimgl
                "scene.py",
                scene_name,
                quality_flag,
                "-w"              # The -w flag is correct for manimgl
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
                    return {
                        "status": "FAILURE",
                        "message": "Manim render failed. Output file not found after execution.",
                        "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                    }
                output_file_path = alt_path

            destination_blob_name = f"{scene_name}.mp4"
            public_url = upload_to_gcs(output_file_path, GCS_BUCKET_NAME, destination_blob_name)

            return {
                "status": "success",
                "url": public_url,
                "logs": stdout
            }

    except Exception as e:
        return {
            "status": "FAILURE",
            "message": f"An unexpected error occurred in the render task: {str(e)}",
            "logs": ""
        }