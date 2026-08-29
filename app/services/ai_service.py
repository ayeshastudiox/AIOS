import json
from groq import Groq
from app.config import settings

def generate_insights_from_metrics(metrics: dict) -> dict:
    """
    Sends business metrics to Groq LLM API and returns structured AI insights.
    """
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing. Please ensure it is set in environment variables or .env file.")

    client = Groq(api_key=settings.GROQ_API_KEY)

    prompt = f"""
    You are an expert business analytics consultant. Analyze the following business metrics:
    {json.dumps(metrics, indent=2)}

    Provide a JSON response with exactly two keys:
    1. "insights": A summary of key takeaways and performance trends.
    2. "recommendations": Actionable strategic advice based on the metrics.

    Do not include any extra text outside the valid JSON object.
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "insights": content,
            "recommendations": "Could not parse structured recommendations. Please review raw output."
        }
    except Exception as e:
        raise RuntimeError(f"Error calling Groq API: {str(e)}")