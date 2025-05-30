# tests/test_interactions.py
import json
import time

import pytest
from nacl.signing import SigningKey

from main import app  # your Flask app

# Generate a test keypair once
TEST_SK = SigningKey.generate()
TEST_PK = TEST_SK.verify_key.encode().hex()


@pytest.fixture(autouse=True)
def set_test_public_key(monkeypatch):
    # Point your code at the test key
    monkeypatch.setenv("DISCORD_PUBLIC_KEY", TEST_PK)
    yield


@pytest.fixture
def client():
    return app.test_client()


def sign(body: bytes, timestamp: str) -> str:
    # Discord signs timestamp+body with its private key
    msg = timestamp.encode() + body
    return TEST_SK.sign(msg).signature.hex()


def make_headers(body: bytes):
    ts = str(int(time.time()))
    return {
        "X-Signature-Ed25519": sign(body, ts),
        "X-Signature-Timestamp": ts,
        "Content-Type": "application/json",
        "Content-Length": str(len(body)),
    }


def test_ping(client):
    payload = json.dumps({"type": 1}).encode()
    resp = client.post("/", data=payload, headers=make_headers(payload))
    assert resp.status_code == 200
    assert resp.get_json() == {"type": 1}


def test_roll_endpoint(client, monkeypatch):
    # stub out dice
    monkeypatch.setattr("trophybot.dice.roll", lambda: 4)
    body = json.dumps(
        {
            "type": 2,
            "data": {"name": "roll"},
        }
    ).encode()
    resp = client.post("/", data=body, headers=make_headers(body))
    assert resp.status_code == 200
    data = resp.get_json()
    # type 4 = CHANNEL_MESSAGE_WITH_SOURCE
    assert data["type"] == 4
    assert data["data"]["content"] == "🎲 You rolled: 4"
