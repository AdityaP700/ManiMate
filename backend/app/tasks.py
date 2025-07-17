# app/tasks.py
import subprocess
import tempfile
import os
import sys  # <--- IMPORT SYS
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    Celery task to render a Manim scene using an absolute path to manimgl.
    This is the most robust way to ensure the command is found.
    """
    try:
        # --- THIS IS THE BULLETPROOF WAY TO FIND MANIMGL ---
        # Get the directory of the current python executable (e.g., .../venv/Scripts/)
        python_executable_dir = os.path.dirname(sys.executable)
        # Construct the full path to the manimgl executable
        manimgl_path = os.path.join(python_executable_dir, 'manimgl')

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(manim_code)

            QUALITY_FLAGS = {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qk"}
            quality_flag = QUALITY_FLAGS.get(quality, "-ql")

            # Use the full, absolute path to manimgl
            command = [
                manimgl_path,
                "scene.py", # manimgl needs the file name, not the full path when using cwd
                scene_name,
                quality_flag,
                "-w"
            ]

            process = subprocess.Popen(
                command,
                cwd=temp_dir,  # Execute the command from within the temporary directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8' # Be explicit about encoding
            )

            stdout, stderr = process.communicate()
            
            # manimgl's default output path relative to the cwd
            output_file_path = os.path.join(temp_dir, "media", "videos", "scene", quality_flag.replace('-', ''), f"{scene_name}.mp4")

            if not os.path.exists(output_file_path):
                alt_path = os.path.join(temp_dir, "media", "videos", "scene", "1080p60", f"{scene_name}.mp4")
                 # Sometimes the quality is not in the path for manimgl, check the 1080p60 default
                if not os.path.exists(alt_path):
                    return {
                        "status": "FAILURE",
                        "message": "Manim render failed. Output file not found in expected directory.",
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