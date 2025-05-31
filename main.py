import os
import sys
import time

from dotenv import load_dotenv
from flask import Flask, request
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

load_dotenv()

app = Flask(__name__)

# Allow importing trophybot package from src directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import trophybot.dice as dice  # noqa: E402


def trophybot(request):
    """Discord interactions HTTP endpoint."""
    DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
    # Debugging: log public key and incoming headers
    print("DEBUG: DISCORD_PUBLIC_KEY =", DISCORD_PUBLIC_KEY)
    print("DEBUG: X-Signature-Ed25519 =", request.headers.get("X-Signature-Ed25519"))
    print(
        "DEBUG: X-Signature-Timestamp =", request.headers.get("X-Signature-Timestamp")
    )
    print("DEBUG: Content-Length =", request.headers.get("Content-Length"))
    print("DEBUG: Body snippet =", request.get_data(as_text=True)[:200])
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
        message = f"{timestamp}{body}".encode()
        verify_key.verify(bytes.fromhex(signature) + message)
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
        if name == "roll":
            result = dice.roll()
            return {"type": 4, "data": {"content": f"🎲 You rolled: {result}"}}
        return {"type": 4, "data": {"content": f"Unknown command: {name}"}}

    return {}


@app.route("/", methods=["POST"])
def interactions():
    """Flask route for Discord interactions."""
    return trophybot(request)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
