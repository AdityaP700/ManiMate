import re

def extract_code_from_response(text: str) -> str:
    blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return "\n".join(blocks).strip() if blocks else text.strip()

def is_valid_manim_code(code: str) -> bool:
    return all(keyword in code for keyword in ["Scene", "construct", "class"])
