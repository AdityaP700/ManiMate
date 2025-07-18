# manual_test.py
import subprocess
import os
import sys

# We use the AI-generated code that we know is good
MANIM_CODE = """
from manim import *

class PythagoreanTheoremScene(Scene):
    def construct(self):
        a = 3
        b = 4
        c = 5

        square_a = Square(side_length=a, color=BLUE)
        square_b = Square(side_length=b, color=GREEN)
        square_c = Square(side_length=c, color=RED)

        formula = MathTex(r"a^2 + b^2 = c^2")

        group_squares = VGroup(square_a, square_b, square_c)
        group_squares.arrange(RIGHT, buff=1)

        self.play(Create(square_a), Create(square_b))
        self.wait(1)
        self.play(Create(square_c))
        self.wait(1)
        self.play(group_squares.arrange(DOWN, buff=1))
        self.wait(1)
        self.play(Write(formula))
        self.wait(2)
"""

SCENE_NAME = "PythagoreanTheoremScene"
TEST_DIR = "test_render"

def run_manual_render():
    """
    A standalone function to replicate the render process outside of Celery.
    """
    print("--- Starting Manual Render Test ---")

    # Ensure the test directory exists
    os.makedirs(TEST_DIR, exist_ok=True)
    scene_file_path = os.path.join(TEST_DIR, "scene.py")

    # Write the code to the file
    with open(scene_file_path, "w") as f:
        f.write(MANIM_CODE)
    print(f"1. Scene code written to {scene_file_path}")

    # Use the same Python that is running this script
    python_executable = sys.executable
    print(f"2. Using Python interpreter: {python_executable}")

    # The exact command we want to test
    command = [
        python_executable,
        "-m", "manimlib",
        "scene.py",
        SCENE_NAME,
        "-w", # Write to file
        "-p", # Skip Preview
        "-ql",# Low quality
    ]
    print(f"3. Assembling command: {' '.join(command)}")

    # Execute the command from within the test directory
    print("\n--- 4. EXECUTING MANIMGL ---")
    process = subprocess.Popen(
        command,
        cwd=TEST_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    stdout, stderr = process.communicate()
    print("--- MANIMGL EXECUTION FINISHED ---\n")

    print("--- 5. RESULTS ---")
    print("\n--- STDOUT (Standard Output): ---")
    print(stdout)
    print("\n--- STDERR (Standard Error): ---")
    print(stderr)
    
    # Check if the video was created
    output_file = os.path.join(TEST_DIR, "media", "videos", "scene", "l", f"{SCENE_NAME}.mp4")
    if os.path.exists(output_file):
        print(f"\n\nSUCCESS! Video file created at: {os.path.abspath(output_file)}")
    else:
        print("\n\nFAILURE. The render process did not create a video file.")

if __name__ == "__main__":
    run_manual_render()