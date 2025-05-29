import os
import sys
import time

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

# Allow importing trophybot package from src directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from trophybot.dice import roll_d6

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")


def trophybot(request):
    """Google Cloud Function entry point for Discord slash command."""
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    if signature is None or timestamp is None or DISCORD_PUBLIC_KEY is None:
        return ("Unauthorized", 401)

    max_size = 8 * 1024
    content_len = request.headers.get("Content-Length")
    if content_len is None or int(content_len) > max_size:
        return ("Payload too large", 413)
    body = request.get_data(as_text=True)
    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
    except (BadSignatureError, ValueError, TypeError):
        return ("Invalid request signature", 401)

    try:
        req_ts = int(timestamp)
    except ValueError:
        return ("Invalid request timestamp", 401)
    if abs(time.time() - req_ts) > 5:
        return ("Stale request timestamp", 401)

    payload = request.get_json(silent=True)
    if not payload:
        return ("Bad Request", 400)

    # Ping request
    if payload.get("type") == 1:
        return {"type": 1}

    # Application command request
    if payload.get("type") == 2:
        data = payload.get("data", {})
        name = data.get("name")
        if name == "roll_d6":
            result = roll_d6()
            return {"type": 4, "data": {"content": f"🎲 You rolled: {result}"}}
        return {"type": 4, "data": {"content": f"Unknown command: {name}"}}

    return {}
