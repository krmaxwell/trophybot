import os
import sys
import time
from types import SimpleNamespace

from dotenv import load_dotenv
from flask import Flask, request
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

load_dotenv()

app = Flask(__name__)

# Allow importing trophybot package from src directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from trophybot.bot import roll_command  # noqa: E402


def _verify_discord_request(current_request):
    """Verify the incoming request from Discord."""
    DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
    signature = current_request.headers.get("X-Signature-Ed25519")
    timestamp = current_request.headers.get("X-Signature-Timestamp")

    if signature is None or timestamp is None or DISCORD_PUBLIC_KEY is None:
        print("DEBUG: Missing signature/timestamp/public_key")
        return ("Unauthorized", 401)

    # Max size check for body
    max_size = 8 * 1024  # 8KB
    content_len_str = current_request.headers.get("Content-Length")
    if content_len_str:
        try:
            content_len = int(content_len_str)
            if content_len > max_size:
                print(f"DEBUG: Payload too large: {content_len} bytes")
                return ("Payload too large", 413)
        except ValueError:
            print(f"DEBUG: Invalid Content-Length: {content_len_str}")
            return ("Bad Request", 400)
    # else: Consider if missing Content-Length should be an error.
    # For now, proceed as Discord should send it.

    body = current_request.get_data(as_text=True)  # Get body for signature verification
    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        message_to_verify = f"{timestamp}{body}".encode()
        # Assuming existing signature method is correct: signature_bytes + message_bytes
        verify_key.verify(bytes.fromhex(signature) + message_to_verify)
    except (BadSignatureError, ValueError, TypeError) as e:
        print(f"DEBUG: Invalid request signature: {e}")
        return ("Invalid request signature", 401)

    # Timestamp check
    try:
        req_ts = int(timestamp)
    except ValueError:
        print("DEBUG: Invalid request timestamp format")
        return ("Invalid request timestamp", 401)
    if abs(time.time() - req_ts) > 300:  # 5 minutes
        print("DEBUG: Stale request timestamp")
        return ("Stale request timestamp", 401)
    return None  # Verification successful


def _handle_ping_request(_payload):
    """Handle a PING request from Discord."""
    print("DEBUG: Handling PING")
    return {"type": 1}


async def _handle_application_command(payload):
    """Handle an APPLICATION_COMMAND request from Discord."""
    print("DEBUG: Handling Application Command")
    data = payload.get("data", {})
    name = data.get("name")
    print(f"DEBUG: Command name: {name}")

    async def send_message_for_handler(message_content: str):
        print(
            f"DEBUG: send_message_for_handler creating response for: {message_content}"
        )
        return {"type": 4, "data": {"content": message_content}}

    options = data.get("options", [])  # Default to empty list

    interaction_data_obj = SimpleNamespace(options=options)
    fake_interaction_obj = SimpleNamespace(
        response=SimpleNamespace(send_message=send_message_for_handler),
        data=interaction_data_obj,
    )

    if name == "roll":
        print("DEBUG: Routing to roll_command.callback")
        return await roll_command.callback(fake_interaction_obj)

    print(f"DEBUG: Unknown command: {name}")
    return {"type": 4, "data": {"content": f"Unknown command: {name}"}}


@app.route("/", methods=["POST"])
async def interactions():  # Made async
    """Flask route for Discord interactions."""
    verification_result = _verify_discord_request(request)
    if verification_result:
        return verification_result

    # Parse JSON payload *after* signature verification
    payload = request.get_json(silent=True)
    if not payload:
        print("DEBUG: Bad Request, no JSON payload or failed to parse")
        return ("Bad Request", 400)

    # Optional: More detailed debug logging of received valid request
    print(f"DEBUG: Validated request. Payload type: {payload.get('type')}")
    if payload.get("type") == 2:  # Application Command
        print(f"DEBUG: Command data: {payload.get('data')}")

    # Ping request
    if payload.get("type") == 1:
        return _handle_ping_request(payload)

    # Application command request
    if payload.get("type") == 2:
        return await _handle_application_command(payload)

    print("DEBUG: Unhandled payload type or scenario")
    return {}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
