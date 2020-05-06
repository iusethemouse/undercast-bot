# Undercast - A Telegram bot for podcasts
[@undercast_bot](https://t.me/undercast_bot)

A minimalist bot that makes it easy to:
- Search for podcasts using any related term: podcast name, artist, topic, genre.
- Download episodes, which you can then listen to using Telegram's in-app player.
- Share favourite podcasts and episodes with anyone - they are just Telegram messages.

## Planned features
- Subscriptions
- Notifications


# Changelog
__v0.2__ - Added cloud-hosting functionality via webhooks. Implemented a workaround for Bot API's file size restriction using MadelineProto. A secondary process now taps into Telegram API to upload files and provides their file ID to the primary process.

__v0.1__ - Initial release. Search is fully implemented. Files larger than 50MB are split into parts due to Telegram's Bot API restrictions.