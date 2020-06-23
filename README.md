# Undercast - A Telegram bot for podcasts

[@undercast_bot](https://t.me/undercast_bot)

A minimalist bot that makes it easy to:

- Search for podcasts using any related term: podcast name, artist, topic, genre.
- Download episodes, which you can then listen to using Telegram's in-app player.
- Share favourite podcasts and episodes with anyone - they are just Telegram messages.

## Why use Undercast

- __Access from any device with a Telegram client__: download an episode while on your desktop, listen to it on your phone while on the go.
- __It's all messages__: liked an episode? Want to keep track of that link in the show notes? Just forward Undercast messages to your Saved Messages and they will be there for when you need them.
- __Manage storage and mobile data use__: episodes can be streamed, downloaded, and easily deleted to reclaim storage.

## Preview

![Screenshots](https://i.imgur.com/fTEoYgT.jpg)

## How to run locally

Make sure you have a bot token from [@BotFather](https://t.me/BotFather), and Telegram API from [my.telegram.org](https://my.telegram.org/). See [here](https://docs.madelineproto.xyz/docs/LOGIN.html#getting-permission-to-use-the-telegram-api) for help with Telegram API.

Specify the above in `start_bot_local.py` and `start_file_uploader.php`.

[Download](https://getcomposer.org/doc/00-intro.md#locally) `composer.phar` in the bot directory, then run:

```console
$ php composer.phar install
$ pip install -r requirements.txt
$ python start_bot_local.py
```

This will start the primary bot process. In a new `shell` instance, run:

```bash
$ php episode_uploader/start_file_uploader.php
```

This will start the secondary process for acquiring episode file IDs. Upon request, specify that you want to login as a bot, and specify your bot token. After the initial launch, a `.session` file will be generated with the entered parameters, and consequent launches won't require any additional input.

## Changelog

__v0.4.0__ - Added subscriptions.

__v0.3.0__ - Storage is now implemented using an SQLite database, which replaces the [pickle-based persistence solution](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Storing-bot%2C-user-and-chat-related-data) provided by the python-telegram-bot wrapper.

__v0.2.1__ - Added async functionality to the episode download process, which now allows the bot to continue being responsive while awaiting file IDs from the secondary process. Fixed the HTML parser for episode descriptions skipping tags that have additional attributes. Added documentation, improved naming, streamlined and generalised certain routines.

__v0.2.0__ - Added cloud-hosting functionality via webhooks. Implemented a workaround for Bot API's file size restriction using [MadelineProto](https://github.com/danog/MadelineProto). A secondary process now taps into Telegram API to upload files and provides their file ID to the primary process.

__v0.1.0__ - Initial release. Search is fully implemented. Files larger than 50MB are split into parts due to Telegram's Bot API restrictions.

Made with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and [MadelineProto](https://github.com/danog/MadelineProto).
