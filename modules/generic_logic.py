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

- Search for podcasts using any related term: podcast name, artist, topic, genre.
- Download and listen to episodes.
- Share favourite podcasts and episodes with anyone.

To get started, type a search term after the /search command.
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
