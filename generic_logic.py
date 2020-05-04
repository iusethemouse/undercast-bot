# Global imports
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    for k in ['podcasts', 'episodes']:
        if k not in context.bot_data:
            context.bot_data[k] = dict()
    
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
This is <b>Undercast</b>.
- Search and subscribe to podcasts
- Download and share episodes
- Get notified of new releases

To get started, type a search term after the /search command.

Type /help to learn more.


<u>Note:</u>
The subscriptions feature is in development.
Large episodes are currently split into parts due to Telegram's file size restrictions.
""", parse_mode='html')


def echo(update, context):
    # Echo plaintext messages back to confirm that bot is online
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=update.message.text)
    

def not_imp_button(update, context):
    bot = context.bot
    query = update.callback_query
    query.answer()
    
    bot.send_message(chat_id=update.effective_chat.id,
                     text='Feature is not yet implemented.')
    
    
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Unknown command.")
    
    
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update caused error "%s"', context.error)
