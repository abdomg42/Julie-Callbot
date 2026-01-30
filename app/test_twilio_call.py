# Test Twilio call
from twilio_client import make_call

# Make a test call to Twilio webhook
try:
    call = make_call("+19794818707", "https://loraine-araceous-kelsi.ngrok-free.dev/twilio/voice")
    print(f"Call initiated: {call.sid}")
except Exception as e:
    print(f"Error: {e}")