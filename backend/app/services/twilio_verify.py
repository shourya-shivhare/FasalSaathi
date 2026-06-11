import logging
from fastapi import HTTPException, status
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class TwilioVerifyService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.service_sid = settings.TWILIO_VERIFY_SERVICE_SID
        self.client = None
        
        # Only initialize if credentials are provided
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio Client: {e}")
                self.client = None

    def send_otp(self, phone_number: str, channel: str = "sms") -> str:
        """
        Sends an OTP using Twilio Verify service.
        Returns the status (e.g., 'pending') or raises HTTPException.
        """
        if not self.client or not self.service_sid:
            logger.warning("Twilio credentials are not fully configured. Using mock response for development.")
            # While the requirement says "No mock authentication systems", a fallback for local developers
            # is critical when credentials are empty, but we must log a warning.
            # If the user wants strictly no fallback, we raise an error.
            # Let's raise an error if not configured, except in a test environment or if we want to be strict.
            # Wait, let's raise a 500 error if not configured, so the developer knows they must set it.
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Twilio Verify Service is not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_VERIFY_SERVICE_SID in your .env file."
            )

        try:
            verification = self.client.verify.v2.services(self.service_sid).verifications.create(
                to=phone_number,
                channel=channel
            )
            return verification.status
        except TwilioRestException as e:
            logger.error(f"Twilio Verify error sending OTP to {phone_number}: {e}")
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to send OTP via Twilio: {e.msg}"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending OTP to {phone_number}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while sending the OTP."
            )

    def verify_otp(self, phone_number: str, code: str) -> bool:
        """
        Verifies an OTP code using Twilio Verify service.
        Returns True if approved, False otherwise, or raises HTTPException.
        """
        if not self.client or not self.service_sid:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Twilio Verify Service is not configured."
            )

        try:
            verification_check = self.client.verify.v2.services(self.service_sid).verification_checks.create(
                to=phone_number,
                code=code
            )
            return verification_check.status == "approved"
        except TwilioRestException as e:
            logger.error(f"Twilio Verify error checking OTP for {phone_number}: {e}")
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f"Failed to verify OTP via Twilio: {e.msg}"
            )
        except Exception as e:
            logger.error(f"Unexpected error verifying OTP for {phone_number}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while verifying the OTP."
            )

# Central instance
twilio_verify_service = TwilioVerifyService()
