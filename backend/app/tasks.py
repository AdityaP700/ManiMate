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
    Celery task that explicitly sets the PYTHONPATH for the subprocess.
    This is the most robust solution for environment issues in background workers.
    """
    try:
        python_executable = sys.executable
        
        # --- THE DEFINITIVE FIX: Manually construct the PYTHONPATH ---
        # 1. Find the root directory of your virtual environment
        venv_dir = os.path.dirname(os.path.dirname(python_executable))
        # 2. Find the site-packages directory where libraries are installed
        site_packages = os.path.join(venv_dir, 'Lib', 'site-packages')
        
        # 3. Create a clean environment for the subprocess and add the PYTHONPATH
        process_env = os.environ.copy()
        process_env['PYTHONPATH'] = site_packages

        with tempfile.TemporaryDirectory() as temp_dir:
            scene_file_path = os.path.join(temp_dir, "scene.py")
            with open(scene_file_path, "w") as f:
                f.write(manim_code)

            QUALITY_FLAGS = {"low": "-ql", "medium": "-qm", "high": "-qh", "production": "-qk"}
            quality_flag = QUALITY_FLAGS.get(quality, "-ql")

            command = [
                python_executable,
                "-m", "manimlib",
                "scene.py",
                scene_name,
                quality_flag,
                "-w"
            ]

            # 4. Pass the custom environment to the subprocess
            process = subprocess.Popen(
                command,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                env=process_env # <--- Use the environment with the correct PYTHONPATH
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

@celery.task
def debug_environment():
    """
    A diagnostic task to print the execution environment of the Celery worker.
    This helps us understand why modules might not be found.
    """
    print("\n--- CELERY WORKER ENVIRONMENT DEBUG ---")
    
    # 1. Which Python is being used?
    print(f"sys.executable: {sys.executable}")
    
    # 2. Where is this Python looking for modules? (The most important part)
    print("\nsys.path (Python's search paths):")
    for path in sys.path:
        print(f"  - {path}")
        
    # 3. Can we find 'site-packages' correctly?
    venv_dir = os.path.dirname(os.path.dirname(sys.executable))
    site_packages = os.path.join(venv_dir, 'Lib', 'site-packages')
    print(f"\nCalculated site-packages: {site_packages}")
    print(f"Does it exist? {os.path.exists(site_packages)}")

    # 4. Let's try to import manimlib directly here.
    try:
        import manimlib
        print("\nSUCCESS: 'import manimlib' worked inside the task.")
        # If it works, where did it find it?
        print(f"manimlib location: {manimlib.__file__}")
    except ModuleNotFoundError:
        print("\nFAILURE: 'import manimlib' failed inside the task.")
        
    print("--- END DEBUG ---")
    return {"status": "Debug task complete. Check Celery worker logs."}