# app/services/llm.py
import openai
import google.generativeai as genai
from app.config import OPENAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY

def generate_manim_code(prompt: str):
    """
    Generates Manim code from a natural language prompt with a multi-model fallback.
    """
    # 1. Try OpenAI
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",  # Or your preferred model
            prompt=f"Convert the following to a Manim scene: {prompt}",
            max_tokens=1024
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"OpenAI failed: {e}")

    # 2. Fallback to Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"Create a Python script for a Manim animation based on this prompt: {prompt}")
        return response.text.strip()
    except Exception as e:
        print(f"Gemini failed: {e}")

    # 3. Fallback to DeepSeek
    # Add your DeepSeek API call logic here when the library is available
    
    return "# All AI providers failed to generate code."