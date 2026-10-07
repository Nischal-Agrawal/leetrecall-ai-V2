import os
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def generate_ai_advice(
    question,
    forget_probability
):
    prompt = f"""
You are an expert DSA revision coach.

Question:
{question}

Forget Probability:
{forget_probability}

Explain:

1. Why this question should be revised
2. Which topic or pattern may be weak
3. What the student should revise next

Keep response under 120 words.
"""

    try:
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return (
            "AI advice is temporarily unavailable because the "
            "Gemini API rate limit has been reached. "
            "Please wait a minute and try again."
        )