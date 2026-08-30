from groq import Groq
from app.config import settings


def generate_meeting_summary(transcript: str) -> str:
    """
    Generates a structured meeting summary using Groq.
    """

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Please ensure it is set in the .env file."
        )

    if not transcript or not transcript.strip():
        raise ValueError("Meeting transcript cannot be empty.")

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
You are a professional meeting assistant.

Analyze the following meeting transcript and create a clear, structured summary.

Meeting Transcript:
{transcript}

Requirements:
- Return only the meeting summary.
- Do not include explanations or commentary.
- Use exactly these three sections:
  Key Decisions
  Action Items
  Deadlines
- Under each section, use concise bullet points.
- If no information is available for a section, write "None specified."
- Do not invent information that is not present in the transcript.
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
            temperature=0.2,
        )

        result = response.choices[0].message.content

        if not result:
            raise RuntimeError("Groq returned an empty meeting summary.")

        return result.strip()

    except Exception as e:
        raise RuntimeError(
            f"Error generating meeting summary: {str(e)}"
        )