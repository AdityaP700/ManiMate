# app/tasks.py
import subprocess
from celery import Celery
from app.config import REDIS_URL
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task
def render_manim_scene(manim_code: str, scene_name: str):
    """
    A Celery task to render a Manim scene and capture logs if something breaks.
    """

    # Step 1: Save Manim code to a file
    with open("temp_scene.py", "w") as f:
        f.write(manim_code)

    # Step 2: Prepare the Manim command
    command = [
        "manimgl",            # CLI tool for rendering
        "temp_scene.py",      # The file we just created
        scene_name,           # Class name like "MyScene"
        "-ql",                # Quick low quality
        "-w"                  # Write video to disk
    ]

    # Step 3: Run the command and capture output/errors
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # returns strings instead of bytes
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # Something went wrong
            return {
                "status": "error",
                "message": "Manim render failed.",
                "logs": stderr  # Only send error logs
            }

        # Success: Upload the rendered video
        output_file = f"{scene_name}.mp4"
        upload_to_gcs(output_file, "your-gcs-bucket", output_file)

        return {
            "status": "success",
            "file": output_file,
            "logs": stdout  # You can return normal logs too
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
