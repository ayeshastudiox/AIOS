from groq import Groq
from app.config import settings


def generate_business_email(
    recipient: str,
    scenario: str,
    tone: str
) -> str:
    """
    Generates a professional business email using Groq.
    """

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Please ensure it is set in the .env file."
        )

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
You are a professional business communication assistant.

Write a professional business email based on the following information:

Recipient: {recipient}
Scenario: {scenario}
Tone: {tone}

Requirements:
- Write only the email.
- Do not include explanations or commentary.
- Use a clear and professional structure.
- Include an appropriate greeting.
- Clearly address the given scenario.
- Include a suitable closing.
- Do not invent unnecessary facts.
- Do not use markdown formatting.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Error generating business email: {str(e)}")