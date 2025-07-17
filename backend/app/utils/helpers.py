# app/utils/helpers.py

import ast

def extract_scene_name(code: str) -> str:
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if hasattr(base, "id") and base.id == "Scene":
                        return node.name
        return "DefaultScene"
    except Exception as e:
        print("Error extracting scene name:", str(e))
        return "DefaultScene"
