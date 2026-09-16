from app.config import settings
from google import genai

try:
    client = genai.Client(api_key=settings.gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: Gemini connection successful!"
    )

    print(response.text)

except Exception as e:
    print("Gemini connection failed:")
    print(e)