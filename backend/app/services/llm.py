# app/services/llm.py

from openai import OpenAI
import google.generativeai as genai
import re
from app.core.logging import logger
from typing import Dict, Optional, Literal
from app.config import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    DEEPSEEK_API_KEY,
    OPENAI_PROJECT_ID,
    # OPENROUTER_API_KEY,
)

# Enhanced type definitions
QualityLevel = Literal["draft", "polished", "3b1b-style", "minimal"]
StyleType = Literal[
    "educational", "geometric", "algebraic", "calculus", "probability", "linear-algebra"
]
DetailLevel = Literal["basic", "intermediate", "advanced"]
ProviderType = Literal["openai", "gemini", "deepseek", "openrouter", "auto"]

# Clients setup
openai_client = OpenAI(api_key=OPENAI_API_KEY, project=OPENAI_PROJECT_ID)

# openrouter_client = OpenAI(
#     api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1"
# )

deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1"
)

# Enhanced examples with better commenting
EXAMPLE_ALGEBRA = """
from manim import *

class PythagoreanProof(Scene):
    def construct(self):
        # Step 1: Introduce the theorem
        title = Title("Visual Proof of the Pythagorean Theorem")
        self.play(Write(title))

        # Step 2: Set up the triangle dimensions
        a, b = 2.0, 3.0
        c = np.sqrt(a**2 + b**2)

        # Step 3: Create visual squares representing a² and b²
        sq_a = Square(side_length=a, fill_color=BLUE,
                      fill_opacity=0.8).shift(LEFT * (b/2 + a/2))
        sq_b = Square(side_length=b, fill_color=GREEN,
                      fill_opacity=0.8).next_to(sq_a, RIGHT, buff=0)

        # Step 4: Add the right triangle to complete the visual
        triangle = Polygon(sq_a.get_corner(UR), sq_b.get_corner(UL), sq_b.get_corner(DL),
                          stroke_color=WHITE, fill_color=YELLOW, fill_opacity=0.8)

        self.play(Create(sq_a), Create(sq_b), run_time=1.5)
        self.play(Create(triangle))

        # Step 5: Visual transformation showing a² + b² = c²
        rearranged_group = VGroup(sq_a.copy(), sq_b.copy())
        sq_c = Square(side_length=c, fill_color=RED, fill_opacity=0.8)

        self.play(Transform(rearranged_group, sq_c))

        # Step 6: Display the mathematical conclusion
        formula = MathTex("a^2", "+", "b^2", "=",
                          "c^2").next_to(title, DOWN, buff=0.5)
        formula[0].set_color(BLUE)
        formula[2].set_color(GREEN)
        formula[4].set_color(RED)
        self.play(Write(formula))
        self.wait(2)
"""

EXAMPLE_CALCULUS = """
from manim import *

class DerivativeVisualization(Scene):
    def construct(self):
        # Step 1: Set up coordinate system
        axes = Axes(x_range=[-4, 4, 1], y_range=[-1, 7, 1],
                    axis_config={"color": BLUE})
        parabola = axes.plot(lambda x: x**2, color=WHITE, stroke_width=3)

        # Step 2: Create dynamic tracking system
        x_tracker = ValueTracker(-2)

        # Step 3: Define the tangent line that updates dynamically
        tangent_line = always_redraw(
            lambda: axes.get_secant_slope_group(
                x=x_tracker.get_value(),
                graph=parabola,
                dx=0.01,
                secant_line_color=YELLOW,
                secant_line_length=4,
            )
        )

        # Step 4: Add a tracking dot
        tracking_dot = always_redraw(
            lambda: Dot(color=RED).move_to(
                axes.c2p(x_tracker.get_value(), x_tracker.get_value()**2)
            )
        )

        # Step 5: Build the scene progressively
        self.play(Create(axes), Create(parabola))
        self.play(Create(tracking_dot), Create(tangent_line))
        self.wait(1)

        # Step 6: Animate the key insight - derivative as slope
        self.play(x_tracker.animate.set_value(2), run_time=5)

        # Step 7: Add explanatory text
        explanation = Text(
            "Derivative = Slope of Tangent Line", font_size=24).to_edge(UP)
        self.play(Write(explanation))
        self.wait(2)
"""

# Enhanced prompt template with quality-aware instructions
ENHANCED_PROMPT_TEMPLATE = """
You are an expert Manim developer and visual educator in the style of 3Blue1Brown. Generate a complete Python script for a Manim Community animation.

**ANALYSIS PHASE - Follow this Chain of Thought:**

1. **Concept Deconstruction**: What mathematical concept needs visualization?
2. **Visual Insight Discovery**: What's the "aha!" moment that makes this concept click?
3. **Educational Flow Planning**: How should the explanation unfold step-by-step?
4. **Pattern Recognition**: Which animation template best fits this concept?

**QUALITY REQUIREMENTS:**
- Quality Level: {quality}
- Style Focus: {style}
- Detail Level: {detail_level}

**Quality Level Guidelines:**
- **draft**: Basic visualization, minimal comments
- **polished**: Smooth animations, clear explanations, good pacing
- **3b1b-style**: Elegant visual storytelling, multiple "reveal" moments
- **minimal**: Simple, clean, focused on core concept

**Style Focus Guidelines:**
- **educational**: Emphasize step-by-step learning
- **geometric**: Focus on shapes, transformations, spatial relationships
- **algebraic**: Show equation manipulations and symbolic reasoning
- **calculus**: Demonstrate limits, derivatives, integrals with dynamic elements
- **probability**: Use histograms, distributions, random processes
- **linear-algebra**: Vectors, matrices, transformations, basis changes

**TECHNICAL REQUIREMENTS:**
- Import: `from manim import *` only
- Class name must be descriptive and CamelCase
- Add step-by-step comments explaining the educational purpose
- Use meaningful variable names
- Include proper timing with `run_time` and `wait()`
- Color code related elements for visual clarity
-**CRITICAL: For all `MathTex` objects, ensure the string is a raw string (e.g., `r"..."`) and that all LaTeX syntax is 100% valid. Double-check all backslashes and special characters.**
-**CRITICAL: To set the color of a mobject created by a helper method (like `Brace.get_tex` or `Axes.get_graph_label`), you must do it in two steps. First, create the object. Second, set its color. Example: `label = brace.get_tex("My Label"); label.set_color(BLUE)`**

**Animation Patterns Available:**
- Dynamic function plotting with `always_redraw()`
- Geometric transformations and morphing
- Step-by-step equation derivations
- Interactive elements with `ValueTracker`
- Progressive revelation techniques
- Mathematical theorem proofs

**Examples:**

**Example 1: Geometric Proof**
```python
{example_algebra}
```

**Example 2: Calculus Concept**
```python
{example_calculus}
```

**User Request**: {user_prompt}

**Generate the complete, educational Python script now:**
"""


def extract_python_code(text: str) -> str:
    """Extract Python code from various markdown formats with robust fallbacks."""
    # Try standard markdown code blocks first
    patterns = [
        r"```python\n(.*?)```",
        r"```\n(.*?)```",
        r"`(.*?)`",
        r"(?:^|\n)(from manim import.*?)(?:\n\n|\Z)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1).strip()
            if "from manim import" in code:
                return code

    # If no patterns match, return the text but clean it
    lines = text.split("\n")
    code_lines = []
    in_code = False

    for line in lines:
        if line.strip().startswith("from manim import"):
            in_code = True
        if in_code:
            code_lines.append(line)
        if in_code and line.strip() == "" and len(code_lines) > 10:
            # Likely end of code block
            break

    return "\n".join(code_lines) if code_lines else text.strip()


def validate_manim_code(code: str) -> tuple[bool, str]:
    """Basic validation of generated Manim code."""
    if not code or len(code.strip()) < 50:
        return False, "Code too short or empty"

    required_elements = [
        "from manim import *",
        "class",
        "def construct(self):",
        "self.play(",
    ]

    for element in required_elements:
        if element not in code:
            return False, f"Missing required element: {element}"

    # Check for common issues
    if "import numpy" in code or "import math" in code:
        return False, "Should only import from manim"

    return True, "Code appears valid"


# app/services/llm.py

def generate_manim_code(
    prompt: str,
    quality: QualityLevel = "polished",
    style: StyleType = "educational",
    detail_level: DetailLevel = "intermediate",
    preferred_provider: ProviderType = "auto",
    api_keys: Dict[str, Optional[str]] = {},
) -> dict:
    """
    Generate Manim code with enhanced parameters, validation, and robust error handling.
    """
    full_prompt = ENHANCED_PROMPT_TEMPLATE.format(
        user_prompt=prompt,
        quality=quality,
        style=style,
        detail_level=detail_level,
        example_algebra=EXAMPLE_ALGEBRA.strip(),
        example_calculus=EXAMPLE_CALCULUS.strip(),
    )

    providers_to_try = []
    if preferred_provider == "auto":
        providers_to_try = [p for p, key in api_keys.items() if key]
        # Add system keys as a final, final fallback if you have them configured
        if GEMINI_API_KEY: providers_to_try.append("gemini")
        if DEEPSEEK_API_KEY: providers_to_try.append("deepseek")
    else:
        providers_to_try = [preferred_provider]
    
    providers_to_try = list(dict.fromkeys(providers_to_try))

    if not providers_to_try and not any([GEMINI_API_KEY, DEEPSEEK_API_KEY]):
         return {"success": False, "validation_result": "No API key provided or configured."}

    last_error = "No providers were available or attempted."
    
    for provider in providers_to_try:
        try:
            print(f"Attempting to generate code with {provider}...")
            raw_text = ""
            
            # Use the user's key if provided, otherwise fall back to the system key from config.py
            user_key = api_keys.get(provider)
            
            if provider == "openai":
                client = OpenAI(api_key=user_key or OPENAI_API_KEY)
                response = client.chat.completions.create(...) # your OpenAI call
                raw_text = response.choices[0].message.content
                
            elif provider == "gemini":
                # **FIX #1: Handle Gemini's unique response structure**
                gemini_key = user_key or GEMINI_API_KEY
                if not gemini_key: continue # Skip if no key is available
                
                genai.configure(api_key=gemini_key)
                # Using a list of models to try is more robust
                models_to_try = ['gemini-2.5-pro', 'gemini-1.5-flash-latest']
                for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(full_prompt)
                        raw_text = response.text
                        break # Success, exit the inner loop
                    except Exception as model_error:
                        print(f"Gemini model '{model_name}' failed: {model_error}")
                        raw_text = "" # Ensure raw_text is empty on failure
                if not raw_text:
                    raise Exception("All Gemini models failed.")

            elif provider == "deepseek":
                deepseek_key = user_key or DEEPSEEK_API_KEY
                if not deepseek_key: continue
                
                client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com/v1")
                response = client.chat.completions.create(...) # your DeepSeek call
                raw_text = response.choices[0].message.content
            
            code = extract_python_code(raw_text)
            is_valid, validation_msg = validate_manim_code(code)
            
            if is_valid:
                logger.info(f"'{provider}' succeeded and passed validation.")
                
                # --- ADD THIS LOG MESSAGE ---
                logger.debug(f"--- Generated Code from {provider} ---\n{code}\n--------------------")
                
                return {
                    "code": code,
                    "provider_used": provider,
                    "validation_result": validation_msg,
                    "success": True
                }
            else:
                last_error = f"'{provider}' generated invalid code: {validation_msg}"
                print(last_error)
                
        except Exception as e:
            # **FIX #2: Correctly capture the error**
            last_error = f"'{provider}' API call failed: {e}"
            print(last_error)

    return {
        "code": f"# All AI providers failed.\n# Last error: {last_error}",
        "provider_used": "none",
        "validation_result": f"All providers failed. Last error: {last_error}",
        "success": False
    }


# Convenience functions for common use cases
def generate_algebra_visualization(prompt: str) -> dict:
    """Generate algebra-focused visualization."""
    return generate_manim_code(prompt, quality="polished", style="algebraic")


def generate_calculus_visualization(prompt: str) -> dict:
    """Generate calculus-focused visualization."""
    return generate_manim_code(prompt, quality="polished", style="calculus")


def generate_geometry_visualization(prompt: str) -> dict:
    """Generate geometry-focused visualization."""
    return generate_manim_code(prompt, quality="3b1b-style", style="geometric")


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced system
    test_prompts = [
        {
            "prompt": "Show the area of a circle is πr² by unwrapping it into a triangle",
            "quality": "3b1b-style",
            "style": "geometric",
        },
        {
            "prompt": "Visualize the quadratic formula derivation step by step",
            "quality": "polished",
            "style": "algebraic",
        },
    ]

    for test in test_prompts:
        print(f"\nTesting: {test['prompt']}")
        result = generate_manim_code(**test)
        print(f"Success: {result['success']}")
        print(f"Provider: {result['provider_used']}")
        print(f"Validation: {result['validation_result']}")
