# app/tasks.py
import subprocess
import tempfile
import os
import sys
from celery import Celery
from app.config import REDIS_URL, GCS_BUCKET_NAME
from app.storage.gcs import upload_to_gcs

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

# Your debug_environment task can stay or be removed.

@celery.task(bind=True)
def render_manim_scene(self, manim_code: str, scene_name: str, quality: str = "low"):
    """
    [DIAGNOSTIC VERSION] This task is temporarily modified to run a very
    simple command to test the ManimGL execution environment itself.
    """
    try:
        python_executable = sys.executable

        # --- TEMPORARY DIAGNOSTIC COMMAND ---
        # We are ignoring the manim_code for this test and just running
        # the simplest possible command to see if ManimGL starts correctly.
        command = [
            python_executable,
            "-m", "manimlib",
            "--version",
        ]

        print(f"Executing diagnostic command: {' '.join(command)}")

        process = subprocess.Popen(
            command,
            # No temp directory or special environment needed for this simple command
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        stdout, stderr = process.communicate()
        
        # This task is EXPECTED to fail here because no video is created.
        # We only care about the logs that it returns.
        return {
            "status": "DIAGNOSTIC_FAILURE",
            "message": "This is an expected failure. Please check the logs.",
            "logs": f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
        }

    except Exception as e:
        return {
            "status": "FAILURE",
            "message": f"An unexpected error occurred in the diagnostic task: {str(e)}",
            "logs": ""
        }