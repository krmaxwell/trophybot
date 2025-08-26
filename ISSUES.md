# Discord API Compatibility Issues

## Moderate Issues

- **Missing interaction response types** - Only returns type 4 (CHANNEL_MESSAGE_WITH_SOURCE), no support for deferred responses

## Minor Issues

- **Debug prints in production** - Extensive debug logging should be conditional (throughout main.py)
- **No rate limit handling** - Command registration in deploy.py doesn't handle Discord API rate limits
- **Missing content-type validation** - Doesn't verify `application/json` content type before parsing
