# Discord API Compatibility Issues

## Critical Issues

• **Incorrect signature verification** - Uses `verify_key.verify(bytes.fromhex(signature) + message_to_verify)` instead of correct `verify_key.verify(message_to_verify, bytes.fromhex(signature))` format (main.py:51)

• **Wrong message format for verification** - Should be `f"{timestamp}{body}".encode()` not concatenated bytes (main.py:49-51)

• **Missing async Flask configuration** - Uses `@app.route` decorator with async function but Flask needs async mode setup

• **No command registration mechanism** - Bot has slash commands defined in deploy.py but no automatic registration on startup

## Moderate Issues

• **Hardcoded API version** - Uses Discord API v10 without version checking (deploy.py:28)  

• **Missing interaction response types** - Only returns type 4 (CHANNEL_MESSAGE_WITH_SOURCE), no support for deferred responses

• **No error handling for malformed payloads** - JSON parsing fails silently, returns generic 400 (main.py:115-117)

• **Timestamp validation too strict** - 5-minute window may be too short for some deployment scenarios (main.py:62)

## Minor Issues

• **Debug prints in production** - Extensive debug logging should be conditional (throughout main.py)

• **No rate limit handling** - Command registration in deploy.py doesn't handle Discord API rate limits

• **Missing content-type validation** - Doesn't verify `application/json` content type before parsing

• **Weak input validation** - Combat command accepts any integer values without bounds checking (bot.py:94-95)