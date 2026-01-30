import os
from fastapi import APIRouter, Request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

router = APIRouter()

# Read credentials from environment variables (safer than hardcoding)
TWILIO_SID = "AC6f072b12c32a4da60885a8d78615f012"
TWILIO_TOKEN = "66732f5d7db9b5b07ad45de2e5348f68"
TWILIO_FROM = "+19794818707"

if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
    # Do not raise on import to keep fastapi/uvicorn from crashing; print a clear warning.
    print("[twilio_client] WARNING: Twilio env vars not set. set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM")

client = Client(TWILIO_SID, TWILIO_TOKEN) if (TWILIO_SID and TWILIO_TOKEN) else None

def make_call(to_number: str, webhook_url: str):
    if client is None:
        raise RuntimeError("Twilio client not initialized - set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
    return client.calls.create(
        to=to_number,
        from_=TWILIO_FROM,
        url=webhook_url  # Twilio will GET this URL to fetch TwiML for the call
    )

@router.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    # Return TwiML instructing Twilio what to say/do
    resp = VoiceResponse()
    resp.say("Hello, connecting to the bot now.", voice="alice", language="en-US")
    # optionally <Dial> or <Play> or <Record>
    return Response(content=str(resp), media_type="application/xml")


if __name__ == "__main__":
    # Quick sanity check when run directly (won't start a server)
    print("twilio_client module loaded. Use make_call() or include router in FastAPI app.")
