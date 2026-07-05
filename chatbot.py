from google import genai
import time

# Replace with your API Key
client = genai.Client(api_key="AQ.Ab8RN6KcA9cAd9Qm0AiN9BPaumAOopE04t0If6mqRrAyAlXa4g")

def ask_ai(question):

    prompt = f"""
    Explain the following in simple English for a deaf student.

    Question:
    {question}
    """

    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash"
    ]

    for model_name in models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        except Exception:
            time.sleep(2)
            continue

    return """Sorry! The AI server is currently busy.

Please try again in a few minutes.
"""