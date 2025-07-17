#apps/services/validator.py
import ast

def validate_manim_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        print("Syntax is invalid.")
        return False

    bad_imports = ["os", "subprocess", "sys", "shutil"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name in bad_imports:
                    print(f"Bad import found: {name.name}")
                    return False
        elif isinstance(node, ast.ImportFrom):
            if node.module in bad_imports:
                print(f"Bad import from: {node.module}")
                return False

    has_scene = False
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if hasattr(base, 'id') and base.id == "Scene":
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "construct":
                            has_scene = True

    if not has_scene:
        print("No Scene class with construct method found.")
        return False

    return True
