import httpx
from app.config import settings

try:
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "from": settings.email_from,
            "to": [settings.email_to],
            "subject": "AI Job Hunter - Test Email",
            "html": """
                <h2>AI Job Hunter</h2>
                <p>Resend connection successful!</p>
            """
        },
        timeout=30
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

except Exception as e:
    print("Resend connection failed:")
    print(e)