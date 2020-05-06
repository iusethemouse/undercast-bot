# Global imports
from telegram.ext import Updater, PicklePersistence
import logging
import os

# Local imports
from modules.handlers import handlers
from modules.generic_logic import error as error_handler
from modules.entities import Pod, Episode

# Globals
BOT_TOKEN = "your bot token"
HEROKU_APP = "your heroku app name"


def initialise(bot_token, persistence_pickle):
    persistence = PicklePersistence(filename=persistence_pickle)
    up = Updater(token=bot_token, persistence=persistence, use_context=True)
    dp = up.dispatcher

    return up, dp


def add_handlers_to_dp(dp, handlers, error_handler):
    for h in handlers:
        dp.add_handler(h)

    dp.add_error_handler(error_handler)


def start():
    port = os.environ.get('PORT')
    up, dp = initialise(BOT_TOKEN, "undercast.pickle")
    add_handlers_to_dp(dp, handlers, error_handler)

    up.start_webhook(listen="0.0.0.0", port=int(port), url_path=BOT_TOKEN)
    up.bot.setWebhook(f"https://{HEROKU_APP}.herokuapp.com/{BOT_TOKEN}")
    up.idle()


if __name__ == "__main__":
    start()