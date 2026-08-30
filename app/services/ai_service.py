import json
from groq import Groq
from app.config import settings


def generate_insights_from_metrics(metrics: dict) -> dict:
    """
    Sends business metrics to Groq LLM API and returns structured AI insights.
    """

    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Please ensure it is set in environment variables or .env file."
        )

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
You are an expert business analytics consultant.

Analyze the following business metrics:

{json.dumps(metrics, indent=2)}

Return ONLY a valid JSON object with exactly two keys:

{{
    "insights": "A concise summary of the key takeaways and performance trends.",
    "recommendations": [
        "First actionable recommendation",
        "Second actionable recommendation",
        "Third actionable recommendation",
        "Fourth actionable recommendation",
        "Fifth actionable recommendation"
    ]
}}

Important rules:
- The recommendations MUST be a JSON array of strings.
- Provide exactly 5 recommendations.
- Do NOT add numbers such as "1.", "2.", or "3." inside the recommendation text.
- Do NOT include markdown.
- Do NOT include any text outside the JSON object.
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
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()

        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "insights": content,
            "recommendations": [
                "Could not parse structured recommendations. Please review the raw AI output."
            ]
        }

    except Exception as e:
        raise RuntimeError(f"Error calling Groq API: {str(e)}")