# app/services/llm.py
from openai import OpenAI
import google.generativeai as genai
from app.config import OPENAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY

# Initialize the OpenAI client for DeepSeek, as it uses an OpenAI-compatible API
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

# Initialize the standard OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)


EXAMPLE_MANIM_CODE = '''
from manim import *

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
- The code must be compatible with manimgl (NOT manimce). The main import is `from manim import *`.
- Do NOT import or use modules like `os`, `sys`, or `input`.
- All animation logic must be inside the `construct()` method of a Scene subclass.
- The script should only contain the import and the class definition. Do not add any extra code or explanations.
"""

def generate_manim_code(prompt: str):
    """
    Generates Manim code from a natural language prompt with a multi-model fallback.
    Uses few-shot prompting and modern API clients.
    """
    full_prompt = FEW_SHOT_PROMPT_TEMPLATE.format(
        user_prompt=prompt,
        example_code=EXAMPLE_MANIM_CODE.strip()
    )

    # 1. Try OpenAI (using the new v1.0.0+ syntax)
    try:
        print("Attempting to generate code with OpenAI...")
        response = openai_client.chat.completions.create(
            model="gpt-4o", # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates Python code for Manim animations."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        code = response.choices[0].message.content.strip()
        # Clean up potential markdown code blocks
        if code.startswith("```python"):
            code = code[9:]
        if code.endswith("```"):
            code = code[:-3]
        print("OpenAI succeeded.")
        return code.strip()
    except Exception as e:
        print(f"OpenAI failed: {e}")

    # 2. Fallback to Gemini
    try:
        print("Attempting to generate code with Gemini...")
        genai.configure(api_key=GEMINI_API_KEY)
        # Use a current, recommended model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(full_prompt)
        print("Gemini succeeded.")
        return response.text.strip()
    except Exception as e:
        print(f"Gemini failed: {e}")

    # 3. Fallback to DeepSeek
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
        code = response.choices[0].message.content.strip()
        print("DeepSeek succeeded.")
        return code
    except Exception as e:
        print(f"DeepSeek failed: {e}")

    return "# All AI providers failed to generate code."