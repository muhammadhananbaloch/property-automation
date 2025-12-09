from twilio.rest import Client
from config import Config
import time

class SmsService:
    def __init__(self):
        # We verify credentials exist so the app doesn't crash if they are missing
        if Config.TWILIO_SID and Config.TWILIO_TOKEN and Config.TWILIO_PHONE:
            self.client = Client(Config.TWILIO_SID, Config.TWILIO_TOKEN)
            self.from_number = Config.TWILIO_PHONE
            self.enabled = True
        else:
            print("⚠️ Twilio credentials missing in .env. SMS Service is DISABLED.")
            self.enabled = False

    def send_sms(self, to_number, message_body):
        """
        Sends a single SMS.
        Returns: Message SID (Success) or None (Failure).
        """
        if not self.enabled:
            print(f"   [Mock SMS] To: {to_number} | Msg: {message_body}")
            # Return a fake ID so you can test the flow without paying/sending
            return "mock_sid_12345"

        try:
            # Twilio strict formatting: +1 for USA
            # We strip common formatting chars to be safe
            clean_number = str(to_number).strip().replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
            if not clean_number.startswith('+'):
                clean_number = f"+1{clean_number}"

            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=clean_number
            )
            return message.sid
            
        except Exception as e:
            # Common errors: "Unsubscribed recipient", "Invalid number", "Landline"
            print(f"   ❌ SMS Failed to {to_number}: {e}")
            return None
