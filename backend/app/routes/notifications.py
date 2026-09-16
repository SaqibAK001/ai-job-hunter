from fastapi import APIRouter, HTTPException, Header

from app.config import settings
from app.services.email_service import send_email
from app.services.digest_service import send_daily_digest


router = APIRouter()


@router.get("")
async def notification_history():

    return {
        "notifications": []
    }


@router.post("/test")
async def test_notification():

    try:

        result = await send_email(
            subject="AI Job Hunter - Test Email",
            html="""
            <html>
                <body style="font-family: Arial, sans-serif;">

                    <h2>AI Job Hunter</h2>

                    <p>
                        Your email notification system is working.
                    </p>

                    <p>
                        This is a test email from your
                        Autonomous AI Job Hunter.
                    </p>

                </body>
            </html>
            """
        )

        return {
            "status": "success",
            "message": "Test email sent",
            "resend": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Email sending failed: {str(e)}"
        )


@router.post("/digest")
async def test_digest(
    x_cron_secret: str | None = Header(default=None)
):

    if x_cron_secret != settings.cron_secret:

        raise HTTPException(
            status_code=401,
            detail="Invalid scheduler credentials"
        )

    result = await send_daily_digest()

    return result