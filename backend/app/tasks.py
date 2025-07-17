# app/tasks.py
import subprocess
from celery import Celery
from app.config import REDIS_URL
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task
def render_manim_scene(manim_code: str, scene_name: str):
    """
    A Celery task to render a Manim scene asynchronously.
    """
    # Save the generated code to a temporary file
    with open("temp_scene.py", "w") as f:
        f.write(manim_code)

    # Execute manimgl
    output_file = f"{scene_name}.mp4"
    command = [
        "manimgl",
        "temp_scene.py",
        scene_name,
        "-ql",  # for low-quality preview
        "-w" # to write to file
    ]
    
    try:
        subprocess.run(command, check=True)
        # Upload the rendered video to GCS
        upload_to_gcs(output_file, GCS_BUCKET_NAME, output_file)
        return {"status": "success", "file": output_file}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}