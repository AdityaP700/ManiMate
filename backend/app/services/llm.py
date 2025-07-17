#app/services/llm.py
import openai
import google.generativeai as genai
from app.config import OPENAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY

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
- The code must be compatible with manimgl (NOT manimce).
- Do NOT import or use modules like `os`, `sys`, or `input`.
- All animation logic must be inside the `construct()` method of a Scene subclass.
- Follow clean structure. No random print statements.
"""

def generate_manim_code(prompt: str):
    """
    Generates Manim code from a natural language prompt with a multi-model fallback.
    Uses few-shot prompting and strict code constraints.
    """
    full_prompt = FEW_SHOT_PROMPT_TEMPLATE.format(
        user_prompt=prompt,
        example_code=EXAMPLE_MANIM_CODE.strip()
    )

    # 1. Try OpenAI
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use GPT-4 if you have access
            prompt=full_prompt,
            max_tokens=1024,
            temperature=0.7,
            stop=None
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI failed: {e}")

    # 2. Fallback to Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini failed: {e}")

    # 3. Fallback to DeepSeek (pseudo logic)
    # You can implement this similarly once DeepSeek integration is available
    return "# All AI providers failed to generate code."
