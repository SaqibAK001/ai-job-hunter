import httpx

from app.config import settings


RESEND_URL = "https://api.resend.com/emails"


async def send_email(subject: str, html: str):

    headers = {
        "Authorization": f"Bearer {settings.resend_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": settings.email_from,
        "to": [settings.email_to],
        "subject": subject,
        "html": html,
    }

    async with httpx.AsyncClient(timeout=30) as client:

        response = await client.post(
            RESEND_URL,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

        return response.json()