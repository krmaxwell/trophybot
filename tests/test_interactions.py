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


def test_roll_endpoint_no_options(client, monkeypatch):
    """Tests the /roll endpoint with no options (plain /roll)."""
    monkeypatch.setattr(
        "trophybot.dice.roll_d6", lambda: 4
    )  # Mock the correct function
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


def test_roll_endpoint_with_light_and_dark_options(client, monkeypatch):
    """Tests the /roll endpoint with light and dark options."""

    # Mock trophybot.dice.roll_pool to return specific results based on count
    def mock_roll_pool(count):
        if count == 2:  # Expected for light dice
            return [1, 6]
        elif count == 3:  # Expected for dark dice
            return [2, 5, 3]
        pytest.fail(f"Unexpected call to roll_pool with count: {count}")
        return []  # Should not be reached

    monkeypatch.setattr("trophybot.dice.roll_pool", mock_roll_pool)

    payload_data = {
        "type": 2,
        "data": {
            "name": "roll",
            "options": [
                {"name": "light", "value": 2},
                {"name": "dark", "value": 3},
            ],
        },
    }
    body = json.dumps(payload_data).encode()
    resp = client.post("/", data=body, headers=make_headers(body))

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["type"] == 4
    expected_content = "Light 1 6 Dark 2 5 3 => Light 6 is highest"
    assert data["data"]["content"] == expected_content


def test_combat_endpoint(client, monkeypatch):
    monkeypatch.setattr("trophybot.dice.roll_pool", lambda count: [2, 3, 5])

    payload_data = {
        "type": 2,
        "data": {
            "name": "combat",
            "options": [
                {"name": "dark", "value": 3},
                {"name": "endurance", "value": 9},
            ],
        },
    }
    body = json.dumps(payload_data).encode()
    resp = client.post("/", data=body, headers=make_headers(body))

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["type"] == 4
    expected_content = (
        "Dice: 2 3 5\n"
        "Top 2: 3+5 = 8\n"
        "Outcome: Failure (< 9)\n"
        "If any die matches your weak point, mark Ruin"
    )
    assert data["data"]["content"] == expected_content
