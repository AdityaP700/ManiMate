import subprocess
from pathlib import Path

import tempfile

def render_manim_code(code: str, scene_name="Scene") -> Path:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        code_file = tmp_path / "scene.py"
        code_file.write_text(code)

        output_file = tmp_path / "output.mp4"

        cmd = [
            "manimgl", str(code_file),
            "-w",  # Write to file
            "-o", str(output_file.name)
        ]
        subprocess.run(cmd, cwd=tmp_path, check=True)
        return output_file
