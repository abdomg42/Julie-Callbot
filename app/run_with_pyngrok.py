import sys
import os
from pyngrok import ngrok
import uvicorn

# Add parent directory to Python path to find core and tool_router modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PORT = 3000

try:
    tunnel = ngrok.connect(PORT, "http")
    print("PUBLIC URL:", tunnel.public_url, flush=True)
    print("WEBHOOK URL:", tunnel.public_url + "/vapi-webhook", flush=True)
except Exception as e:
    print("NGROK ERROR:", repr(e), flush=True)
    raise

uvicorn.run("main_webhook:app", host="0.0.0.0", port=PORT, log_level="info")