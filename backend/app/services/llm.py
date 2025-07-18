# app/services/llm.py

from openai import OpenAI
import google.generativeai as genai
import re
from app.config import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    DEEPSEEK_API_KEY,
    OPENAI_PROJECT_ID,
    OPENROUTER_API_KEY
)

# Clients setup
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    project=OPENAI_PROJECT_ID
)

openrouter_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

EXAMPLE_MANIM_CODE = '''
from manimlib import *

class PiFormulaScene(Scene):
    def construct(self):
        title = Text("The Formula for PI")
        formula = MathTex(r"\\pi = 4 \\sum_{{k=0}}^{{\\infty}} \\frac{{(-1)^k}}{{2k+1}}")
        self.play(Write(title))
        self.play(Create(formula))
        self.wait(2)
'''

FEW_SHOT_PROMPT_TEMPLATE = """
Create a Python script for a manimgl animation based on this prompt: '{user_prompt}'.

Here is a perfect example of the code structure:
---
{example_code}
---

Constraints:
- The code must be compatible with manimgl (NOT manimce). The main import is `from manimlib import *`.
- Do NOT import or use modules like `os`, `sys`, or `input`.
- All animation logic must be inside the `construct()` method of a Scene subclass.
- The script should only contain the import and the class definition. Do not add any extra code or explanations.
"""

def extract_python_code(text):
    match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def generate_manim_code(prompt: str):
    full_prompt = FEW_SHOT_PROMPT_TEMPLATE.format(
        user_prompt=prompt,
        example_code=EXAMPLE_MANIM_CODE.strip()
    )

    # 1. OpenAI (GPT-4o)
    try:
        print("Attempting to generate code with OpenAI...")
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates Python code for Manim animations."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        code = extract_python_code(response.choices[0].message.content)
        print("OpenAI succeeded.")
        return code
    except Exception as e:
        print(f"OpenAI failed: {e}")

    # 2. Gemini
    try:
        print("Attempting to generate code with Gemini...")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(full_prompt)
        code = extract_python_code(response.text)
        print("Gemini succeeded.")
        print("Code returned by Gemini:\n", code)
        return code
    except Exception as e:
        print(f"Gemini failed: {e}")

    # 3. DeepSeek
    try:
        print("Attempting to generate code with DeepSeek...")
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert at generating Manim animation code."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        code = extract_python_code(response.choices[0].message.content)
        print("DeepSeek succeeded.")
        return code
    except Exception as e:
        print(f"DeepSeek failed: {e}")

    # 4. OpenRouter
    try:
        print("Attempting to generate code with OpenRouter...")
        response = openrouter_client.chat.completions.create(
            model="openrouter/openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates Python code for Manim animations."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        code = extract_python_code(response.choices[0].message.content)
        print("OpenRouter succeeded.")
        return code
    except Exception as e:
        print(f"OpenRouter failed: {e}")

    return "# All AI providers failed to generate code."
