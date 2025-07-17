import subprocess
import tempfile
import os
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)


@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    Celery task to render a Manim scene in an isolated temp dir to avoid file collisions.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Save Manim code to a Python file
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(manim_code)

            # 2. Define quality flags
            QUALITY_FLAGS = {
                "low": "-ql",
                "medium": "-qm",
                "high": "-qh",
                "production": "-qk"
            }
            flag = QUALITY_FLAGS.get(quality, "-ql")  # Default to low

            # 3. Prepare and run the Manim command
            command = [
                "manim",
                "scene.py",
                scene_name,
                flag,
                "-o", f"{scene_name}.mp4"
            ]

            process = subprocess.Popen(
                command,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                return {
                    "status": "FAILURE",
                    "message": "Manim render failed.",
                    "logs": stderr
                }

            # 4. Upload to Google Cloud Storage
            output_file_path = os.path.join(temp_dir, f"{scene_name}.mp4")
            destination_blob_name = os.path.basename(output_file_path)

            public_url = upload_to_gcs(
                output_file_path, GCS_BUCKET_NAME, destination_blob_name
            )

            return {
                "status": "success",
                "url": public_url,
                "logs": stdout
            }

    except Exception as e:
        return {
            "status": "FAILURE",
            "message": f"Unexpected error: {str(e)}"
        }
