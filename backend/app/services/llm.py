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

EXAMPLE_ALGEBRA = '''
from manim import *

# A visually intuitive proof of the Pythagorean Theorem
class PythagoreanProof(Scene):
    def construct(self):
        title = Title("Visual Proof of the Pythagorean Theorem")
        self.play(Write(title))
        
        a, b = 2.0, 3.0
        c = np.sqrt(a**2 + b**2)

        # Create squares for a^2 and b^2
        sq_a = Square(side_length=a, fill_color=BLUE, fill_opacity=0.8).shift(LEFT * (b/2 + a/2))
        sq_b = Square(side_length=b, fill_color=GREEN, fill_opacity=0.8).next_to(sq_a, RIGHT, buff=0)
        
        # Create the main right triangle
        triangle = Polygon(sq_a.get_corner(UR), sq_b.get_corner(UL), sq_b.get_corner(DL), stroke_color=WHITE, fill_color=YELLOW, fill_opacity=0.8)
        
        self.play(Create(sq_a), Create(sq_b), run_time=1.5)
        self.play(Create(triangle))
        
        # Show the areas combining into the hypotenuse square
        rearranged_group = VGroup(sq_a.copy(), sq_b.copy())
        sq_c = Square(side_length=c, fill_color=RED, fill_opacity=0.8)
        
        self.play(Transform(rearranged_group, sq_c))
        
        # Display the final formula
        formula = MathTex("a^2", "+", "b^2", "=", "c^2").next_to(title, DOWN, buff=0.5)
        formula[0].set_color(BLUE)
        formula[2].set_color(GREEN)
        formula[4].set_color(RED)
        self.play(Write(formula))
        self.wait(2)
'''

EXAMPLE_CALCULUS = '''
from manim import *

# A visualization of a derivative as the slope of a tangent line
class DerivativeOfParabola(Scene):
    def construct(self):
        axes = Axes(x_range=[-4, 4, 1], y_range=[-1, 7, 1], axis_config={"color": BLUE})
        parabola = axes.plot(lambda x: x**2, color=WHITE)
        
        # Create a tracker for the x-value
        k = ValueTracker(-2)
        
        # Define the tangent line that updates with k
        tangent = always_redraw(
            lambda: axes.get_secant_slope_group(
                x=k.get_value(),
                graph=parabola,
                dx=0.01,
                secant_line_color=YELLOW,
                secant_line_length=4,
            )
        )
        
        dot = always_redraw(
            lambda: Dot().move_to(axes.c2p(k.get_value(), k.get_value()**2))
        )

        self.play(Create(axes), Create(parabola))
        self.play(Create(dot), Create(tangent))
        self.wait(1)
        
        # Animate the tangent moving along the curve
        self.play(k.animate.set_value(2), run_time=5)
        self.wait(2)
'''


# --- NEW: ADVANCED PROMPT TEMPLATE WITH CHAIN OF THOUGHT ---

FEW_SHOT_PROMPT_TEMPLATE = """
You are an expert Manim developer and a visual educator, in the style of 3Blue1Brown. Your task is to generate a single, complete Python script for a Manim Community animation based on the user's prompt. Your output MUST be only the raw Python code.

First, in your reasoning process, you MUST follow this Chain of Thought:
1.  **Deconstruct the Prompt**: What is the core mathematical concept the user wants to visualize? (e.g., a theorem, a function, a transformation).
2.  **Find the "Visual Aha!" Moment**: What is the most clever, intuitive, and elegant way to show this concept? Don't just draw the final result. Animate the *process* that reveals the insight. (e.g., for the area of a circle, unroll it into a triangle).
3.  **Plan the Animation**: List the key visual steps. (e.g., 1. Draw axes. 2. Plot the first curve. 3. Introduce the second curve via a transformation. 4. Display the concluding formula.)
4.  **Identify Common Patterns**: Does the prompt match any common Manim math animation patterns? If so, use those as templates to guide your planning.

Consider these common Manim math animation patterns:
- Equation transformation or stepwise solution
- Dynamic graphing of 1D/2D/3D functions
- Visual proofs of geometric theorems (e.g., Pythagorean, area formulas)
- Demonstrating calculus concepts: limits, derivatives (slope), integrals (area)
- Animated vector or matrix operations in linear algebra
- Probability/statistics visualizations (histograms, distributions, area under curve)
- Transformations: translation, rotation, scaling, reflection
- Morphing between related objects or concepts

If the user prompt matches one of these, use them as templates for your animation planning.

After your reasoning is complete, generate the Python script that executes your plan. The script must follow these rules strictly:
- **Import**: The ONLY import must be `from manim import *`.
- **Code Quality**: The code must be clean, readable, and efficient.
- **Visual Storytelling**: Use `Transform`, `FadeIn`, `Indicate`, `always_redraw`, and other animations to create a dynamic and explanatory story.
- **Accuracy**: The visualization must be mathematically and conceptually sound.

---
Here are examples of the high-quality, educational style you should produce:

**Example 1: Algebra (Pythagorean Theorem)**
```python
{example_algebra}```

**Example 2: Calculus (Derivatives)**
```python
{example_calculus}
User's prompt: '{user_prompt}'

Now, generate the complete Python script.
"""
def extract_python_code(text):
    match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def generate_manim_code(prompt: str):
    full_prompt = FEW_SHOT_PROMPT_TEMPLATE.format(
        user_prompt=prompt,
        example_algebra=EXAMPLE_ALGEBRA.strip(),
        example_calculus=EXAMPLE_CALCULUS.strip()
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
      print("Attempting to generate code with Gemini 2.5 Pro...")
      genai.configure(api_key=GEMINI_API_KEY)  # Ensure this is called before model usage

      model = genai.GenerativeModel('gemini-2.5-pro')
      response = model.generate_content(full_prompt)
      code = extract_python_code(response.text)

      print("Gemini 2.5 Pro succeeded.")
      return code

    except Exception as e:
      print(f"Gemini 2.5 Pro failed: {e}\nTrying Gemini 2.5 Flash...")

    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(full_prompt)
        code = extract_python_code(response.text)

        print("Gemini 2.5 Flash succeeded.")
        return code

    except Exception as e2:
        print(f"Gemini 2.5 Flash failed: {e2}")

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
